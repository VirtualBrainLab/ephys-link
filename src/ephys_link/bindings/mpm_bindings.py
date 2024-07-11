"""Bindings for New Scale Pathfinder MPM HTTP server platform.

MPM works slightly differently than the other platforms since it operates in stereotactic coordinates.
This means exceptions need to be made for its API.

Usage: Instantiate MPMBindings to interact with the New Scale Pathfinder MPM HTTP server platform.
"""

from asyncio import get_running_loop
from json import dumps
from typing import Any

from requests import JSONDecodeError, get, put
from vbl_aquarium.models.unity import Vector3, Vector4

from ephys_link.util.base_bindings import BaseBindings


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

    def __init__(self, port: int) -> None:
        """Initialize connection to MPM HTTP server.

        :param port: Port number for MPM HTTP server.
        :type port: int
        """
        self._url = f"http://localhost:{port}"

    async def get_manipulators(self) -> list[str]:
        return [manipulator["Id"] for manipulator in (await self._query_data())["ProbeArray"]]

    async def get_num_axes(self) -> int:
        return 3

    def get_dimensions(self) -> Vector4:
        return Vector4(x=15, y=15, z=15, w=15)

    async def get_position(self, manipulator_id: str) -> Vector4:
        manipulator_data = await self._manipulator_data(manipulator_id)
        return Vector4(
            x=manipulator_data["Tip_X_ML"],
            y=manipulator_data["Tip_Y_AP"],
            z=manipulator_data["Tip_Z_DV"],
            w=manipulator_data["TIP_Z_DV"],
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

    async def set_position(self, manipulator_id: str, position: Vector4, _: float) -> Vector4:
        requests = {
            "PutId": "ProbeMotion",
            "Probe": self.VALID_MANIPULATOR_IDS.index(manipulator_id),
            "Absolute": 1,
            "Stereotactic": 1,
            "AxisMask": 7,
            "X": position.x,
            "Y": position.y,
            "Z": position.z,
        }
        await self._put_request(requests)

    async def set_depth(self, manipulator_id: str, depth: float, speed: float) -> None:
        """Move the Z axis the needed relative distance to reach the desired depth."""
        # Get current position.
        current_position = await self.get_position(manipulator_id)

        # Compute difference between current and desired depth.
        depth_difference = depth - current_position.z

        # Request movement.
        request = {
            "PutId": "ProbeInsertion",
            "Probe": self.VALID_MANIPULATOR_IDS.index(manipulator_id),
            "Distance": depth_difference,
            "Rate": speed,
        }
        await self._put_request(request)

    async def stop(self, manipulator_id: str) -> None:
        request = {"PutId": "ProbeStop", "Probe": self.VALID_MANIPULATOR_IDS.index(manipulator_id)}
        await self._put_request(request)

    def platform_space_to_unified_space(self, _: Vector4) -> Vector4:
        pass

    def unified_space_to_platform_space(self, _: Vector4) -> Vector4:
        pass

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