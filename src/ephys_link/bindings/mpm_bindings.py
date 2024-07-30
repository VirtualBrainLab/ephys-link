"""Bindings for New Scale Pathfinder MPM HTTP server platform.

MPM works slightly differently than the other platforms since it operates in stereotactic coordinates.
This means exceptions need to be made for its API.

Usage: Instantiate MPMBindings to interact with the New Scale Pathfinder MPM HTTP server platform.
"""

from asyncio import get_running_loop, sleep
from json import dumps
from typing import Any

from requests import JSONDecodeError, get, put
from vbl_aquarium.models.unity import Vector3, Vector4

from ephys_link.util.base_bindings import BaseBindings
from ephys_link.util.common import mmps_to_umps, vector4_to_array


class MPMBinding(BaseBindings):
    """Bindings for New Scale Pathfinder MPM HTTP server platform."""

    # Valid New Scale manipulator IDs
    VALID_MANIPULATOR_IDS = (
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
        "AA",
        "AB",
        "AC",
        "AD",
        "AE",
        "AF",
        "AG",
        "AH",
        "AI",
        "AJ",
        "AK",
        "AL",
        "AM",
        "AN",
    )

    # Movement polling preferences.
    UNCHANGED_COUNTER_LIMIT = 10
    POLL_INTERVAL = 0.2

    def __init__(self, port: int) -> None:
        """Initialize connection to MPM HTTP server.

        :param port: Port number for MPM HTTP server.
        :type port: int
        """
        self._url = f"http://localhost:{port}"
        self._movement_stopped = False

    async def get_manipulators(self) -> list[str]:
        return [manipulator["Id"] for manipulator in (await self._query_data())["ProbeArray"]]

    async def get_axes_count(self) -> int:
        return 3

    def get_dimensions(self) -> Vector4:
        return Vector4(x=15, y=15, z=15, w=15)

    async def get_position(self, manipulator_id: str) -> Vector4:
        manipulator_data = await self._manipulator_data(manipulator_id)
        stage_z = manipulator_data["Stage_Z"]
        return Vector4(
            x=manipulator_data["Stage_X"],
            y=manipulator_data["Stage_Y"],
            z=stage_z,
            w=stage_z,
        )

    async def get_angles(self, manipulator_id: str) -> Vector3:
        manipulator_data = await self._manipulator_data(manipulator_id)

        # Apply PosteriorAngle to Polar to get the correct angle.
        adjusted_polar = manipulator_data["Polar"] - (await self._query_data())["PosteriorAngle"]

        return Vector3(
            x=adjusted_polar if adjusted_polar > 0 else 360 + adjusted_polar,
            y=manipulator_data["Pitch"],
            z=manipulator_data["ShankOrientation"],
        )

    async def get_shank_count(self, manipulator_id: str) -> int:
        return int((await self._manipulator_data(manipulator_id))["ShankCount"])

    def get_movement_tolerance(self) -> float:
        return 0.01

    async def set_position(self, manipulator_id: str, position: Vector4, speed: float) -> Vector4:
        # Duplicate W to Z on target position.
        target_position = position.model_copy(update={"z": position.w})

        # Determine if this is a depth only movement.

        # Get current position to check if this is a depth only movement.
        current_position = await self.get_position(manipulator_id)

        # If X and Y are the same, this is a depth only movement.
        depth_only = (
            abs(current_position.x - target_position.x) <= self.get_movement_tolerance()
            and abs(current_position.y - target_position.y) <= self.get_movement_tolerance()
        )

        # Reset step mode to normal for non-depth only movements.
        if not depth_only:
            await self._put_request(
                {"PutId": "ProbeStepMode", "Probe": self.VALID_MANIPULATOR_IDS.index(manipulator_id), "StepMode": 0}
            )

        # Declare request based on depth only or not.
        # Distance and speed are converted from mm to µm and mm/s to µm/min.
        def _request(current_position_for_request: Vector4) -> dict[str, Any]:
            return (
                {
                    "PutId": "ProbeInsertion",
                    "Probe": self.VALID_MANIPULATOR_IDS.index(manipulator_id),
                    "Distance": mmps_to_umps(current_position_for_request.w - target_position.w),
                    "Rate": mmps_to_umps(speed) * 60,
                }
                if depth_only
                else {
                    "PutId": "ProbeMotion",
                    "Probe": self.VALID_MANIPULATOR_IDS.index(manipulator_id),
                    "Absolute": 1,
                    "Stereotactic": 0,
                    "AxisMask": 7,
                    "X": target_position.x,
                    "Y": target_position.y,
                    "Z": target_position.z,
                }
            )

        await self._put_request(_request(current_position))

        # Keep track of the previous position to check if the manipulator stopped advancing unexpectedly.
        current_position = await self.get_position(manipulator_id)
        previous_position = current_position
        unchanged_counter = 0

        while not self._movement_stopped and not self._is_vector_close(target_position, current_position):
            # Update current position.
            current_position = await self.get_position(manipulator_id)

            # Check if the manipulator is not moving.
            if self._is_vector_close(previous_position, current_position):
                # Position did not change.
                unchanged_counter += 1
            else:
                # Position changed.
                unchanged_counter = 0
                previous_position = current_position

            # Resend request if not moving for too long.
            if unchanged_counter > self.UNCHANGED_COUNTER_LIMIT:
                await self._put_request(_request(current_position))

            # Wait for a short time before checking again.
            await sleep(self.POLL_INTERVAL)

        # Reset movement stopped flag.
        self._movement_stopped = False

        # Return the final position.
        return await self.get_position(manipulator_id)

    async def stop(self, manipulator_id: str) -> None:
        request = {"PutId": "ProbeStop", "Probe": self.VALID_MANIPULATOR_IDS.index(manipulator_id)}
        await self._put_request(request)
        self._movement_stopped = True

    def platform_space_to_unified_space(self, platform_space: Vector4) -> Vector4:
        # unified   <-  platform
        # +x        <-  -x
        # +y        <-  +z
        # +z        <-  +y
        # +w        <-  -w

        return Vector4(
            x=self.get_dimensions().x - platform_space.x,
            y=platform_space.z,
            z=platform_space.y,
            w=self.get_dimensions().w - platform_space.w,
        )

    def unified_space_to_platform_space(self, unified_space: Vector4) -> Vector4:
        # platform  <-  unified
        # +x        <-  -x
        # +y        <-  +z
        # +z        <-  +y
        # +w        <-  -w

        return Vector4(
            x=self.get_dimensions().x - unified_space.x,
            y=unified_space.z,
            z=unified_space.y,
            w=self.get_dimensions().w - unified_space.w,
        )

    # Helper functions.
    async def _query_data(self) -> Any:
        try:
            return (await get_running_loop().run_in_executor(None, get, self._url)).json()
        except ConnectionError as connectionError:
            error_message = f"Unable to connect to MPM HTTP server: {connectionError}"
            raise RuntimeError(error_message) from connectionError
        except JSONDecodeError as jsonDecodeError:
            error_message = f"Unable to decode JSON response from MPM HTTP server: {jsonDecodeError}"
            raise ValueError(error_message) from jsonDecodeError

    async def _manipulator_data(self, manipulator_id: str) -> Any:
        probe_data = (await self._query_data())["ProbeArray"]
        for probe in probe_data:
            if probe["Id"] == manipulator_id:
                return probe

        # If we get here, that means the manipulator doesn't exist.
        error_message = f"Manipulator {manipulator_id} not found."
        raise ValueError(error_message)

    async def _put_request(self, request: dict[str, Any]) -> None:
        await get_running_loop().run_in_executor(None, put, self._url, dumps(request))

    def _is_vector_close(self, target: Vector4, current: Vector4) -> bool:
        return all(abs(axis) <= self.get_movement_tolerance() for axis in vector4_to_array(target - current))
