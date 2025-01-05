"""Bindings for New Scale Pathfinder MPM HTTP server platform.

MPM works slightly differently than the other platforms since it operates in stereotactic coordinates.
This means exceptions need to be made for its API.

Usage: Instantiate MPMBindings to interact with the New Scale Pathfinder MPM HTTP server platform.
"""

from asyncio import get_running_loop, sleep
from json import dumps
from typing import Any, final, override

from requests import JSONDecodeError, get, put
from vbl_aquarium.models.unity import Vector3, Vector4

from ephys_link.utils.base_binding import BaseBinding
from ephys_link.utils.common import scalar_mm_to_um, vector4_to_array


@final
class MPMBinding(BaseBinding):
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
    POLL_INTERVAL = 0.1

    # Speed preferences (mm/s to use coarse mode).
    COARSE_SPEED_THRESHOLD = 0.1
    INSERTION_SPEED_LIMIT = 9_000

    def __init__(self, port: int = 8080) -> None:
        """Initialize connection to MPM HTTP server.

        Args:
            port: Port number for MPM HTTP server.
        """
        self._url = f"http://localhost:{port}"
        self._movement_stopped = False

    @staticmethod
    @override
    def get_display_name() -> str:
        return "Pathfinder MPM Control v2.8.8+"

    @staticmethod
    @override
    def get_cli_name() -> str:
        return "pathfinder-mpm"

    @override
    async def get_manipulators(self) -> list[str]:
        return [manipulator["Id"] for manipulator in (await self._query_data())["ProbeArray"]]  # pyright: ignore [reportAny]

    @override
    async def get_axes_count(self) -> int:
        return 3

    @override
    def get_dimensions(self) -> Vector4:
        return Vector4(x=15, y=15, z=15, w=15)

    @override
    async def get_position(self, manipulator_id: str) -> Vector4:
        manipulator_data: dict[str, float] = await self._manipulator_data(manipulator_id)
        stage_z: float = manipulator_data["Stage_Z"]

        await sleep(self.POLL_INTERVAL)  # Wait for the stage to stabilize.

        return Vector4(
            x=manipulator_data["Stage_X"],
            y=manipulator_data["Stage_Y"],
            z=stage_z,
            w=stage_z,
        )

    @override
    async def get_angles(self, manipulator_id: str) -> Vector3:
        manipulator_data: dict[str, float] = await self._manipulator_data(manipulator_id)

        # Apply PosteriorAngle to Polar to get the correct angle.
        adjusted_polar: int = manipulator_data["Polar"] - (await self._query_data())["PosteriorAngle"]

        return Vector3(
            x=adjusted_polar if adjusted_polar > 0 else 360 + adjusted_polar,
            y=manipulator_data["Pitch"],
            z=manipulator_data["ShankOrientation"],
        )

    @override
    async def get_shank_count(self, manipulator_id: str) -> int:
        return int((await self._manipulator_data(manipulator_id))["ShankCount"])  # pyright: ignore [reportAny]

    @override
    def get_movement_tolerance(self) -> float:
        return 0.01

    @override
    async def set_position(self, manipulator_id: str, position: Vector4, speed: float) -> Vector4:
        # Keep track of the previous position to check if the manipulator stopped advancing.
        current_position = await self.get_position(manipulator_id)
        previous_position = current_position
        unchanged_counter = 0

        # Set step mode based on speed.
        await self._put_request(
            {
                "PutId": "ProbeStepMode",
                "Probe": self.VALID_MANIPULATOR_IDS.index(manipulator_id),
                "StepMode": 0 if speed > self.COARSE_SPEED_THRESHOLD else 1,
            }
        )

        # Send move request.
        await self._put_request(
            {
                "PutId": "ProbeMotion",
                "Probe": self.VALID_MANIPULATOR_IDS.index(manipulator_id),
                "Absolute": 1,
                "Stereotactic": 0,
                "AxisMask": 7,
                "X": position.x,
                "Y": position.y,
                "Z": position.z,
            }
        )

        # Wait for the manipulator to reach the target position or be stopped or stuck.
        while (
            not self._movement_stopped
            and not self._is_vector_close(current_position, position)
            and unchanged_counter < self.UNCHANGED_COUNTER_LIMIT
        ):
            # Wait for a short time before checking again.
            await sleep(self.POLL_INTERVAL)

            # Update current position.
            current_position = await self.get_position(manipulator_id)

            # Check if manipulator is not moving.
            if self._is_vector_close(previous_position, current_position):
                # Position did not change.
                unchanged_counter += 1
            else:
                # Position changed.
                unchanged_counter = 0
                previous_position = current_position

        # Reset movement stopped flag.
        self._movement_stopped = False

        # Return the final position.
        return await self.get_position(manipulator_id)

    @override
    async def set_depth(self, manipulator_id: str, depth: float, speed: float) -> float:
        # Keep track of the previous depth to check if the manipulator stopped advancing unexpectedly.
        current_depth = (await self.get_position(manipulator_id)).w
        previous_depth = current_depth
        unchanged_counter = 0

        # Send move request.
        # Convert mm/s to um/min and cap speed at the limit.
        await self._put_request(
            {
                "PutId": "ProbeInsertion",
                "Probe": self.VALID_MANIPULATOR_IDS.index(manipulator_id),
                "Distance": scalar_mm_to_um(current_depth - depth),
                "Rate": min(scalar_mm_to_um(speed) * 60, self.INSERTION_SPEED_LIMIT),
            }
        )

        # Wait for the manipulator to reach the target depth or be stopped or get stuck.
        while not self._movement_stopped and not abs(current_depth - depth) <= self.get_movement_tolerance():
            # Wait for a short time before checking again.
            await sleep(self.POLL_INTERVAL)

            # Get the current depth.
            current_depth = (await self.get_position(manipulator_id)).w

            # Check if manipulator is not moving.
            if abs(previous_depth - current_depth) <= self.get_movement_tolerance():
                # Depth did not change.
                unchanged_counter += 1
            else:
                # Depth changed.
                unchanged_counter = 0
                previous_depth = current_depth

        # Reset movement stopped flag.
        self._movement_stopped = False

        # Return the final depth.
        return float((await self.get_position(manipulator_id)).w)

    @override
    async def stop(self, manipulator_id: str) -> None:
        request: dict[str, str | int | float] = {
            "PutId": "ProbeStop",
            "Probe": self.VALID_MANIPULATOR_IDS.index(manipulator_id),
        }
        await self._put_request(request)
        self._movement_stopped = True

    @override
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

    @override
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
    async def _query_data(self) -> dict[str, Any]:  # pyright: ignore [reportExplicitAny]
        try:
            # noinspection PyTypeChecker
            return (await get_running_loop().run_in_executor(None, get, self._url)).json()  # pyright: ignore [reportAny]
        except ConnectionError as connectionError:
            error_message = f"Unable to connect to MPM HTTP server: {connectionError}"
            raise RuntimeError(error_message) from connectionError
        except JSONDecodeError as jsonDecodeError:
            error_message = f"Unable to decode JSON response from MPM HTTP server: {jsonDecodeError}"
            raise ValueError(error_message) from jsonDecodeError

    async def _manipulator_data(self, manipulator_id: str) -> dict[str, Any]:  # pyright: ignore [reportExplicitAny]
        probe_data: list[dict[str, Any]] = (await self._query_data())["ProbeArray"]  # pyright: ignore [reportExplicitAny]
        for probe in probe_data:
            if probe["Id"] == manipulator_id:
                return probe

        # If we get here, that means the manipulator doesn't exist.
        error_message = f"Manipulator {manipulator_id} not found."
        raise ValueError(error_message)

    async def _put_request(self, request: dict[str, Any]) -> None:  # pyright: ignore [reportExplicitAny]
        _ = await get_running_loop().run_in_executor(None, put, self._url, dumps(request))

    def _is_vector_close(self, target: Vector4, current: Vector4) -> bool:
        return all(abs(axis) <= self.get_movement_tolerance() for axis in vector4_to_array(target - current)[:3])
