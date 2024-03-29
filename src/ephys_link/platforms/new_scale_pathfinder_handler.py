"""Handle communications with New Scale's HTTP server

Implements New Scale specific API calls.

This is a subclass of :class:`ephys_link.platform_handler.PlatformHandler`.
"""

from __future__ import annotations

import json
from sys import exit
from typing import TYPE_CHECKING
from urllib import request
from urllib.error import URLError

from vbl_aquarium.models.ephys_link import (
    AngularResponse,
    BooleanStateResponse,
    CanWriteRequest,
    DriveToDepthRequest,
    DriveToDepthResponse,
    GotoPositionRequest,
    InsideBrainRequest,
    PositionalResponse,
    ShankCountResponse,
)
from vbl_aquarium.models.unity import Vector3, Vector4

from ephys_link.platform_handler import PlatformHandler

if TYPE_CHECKING:
    import socketio


class NewScalePathfinderHandler(PlatformHandler):
    """Handler for New Scale HTTP server"""

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

    def __init__(self, port: int = 8080) -> None:
        """
        Initialize New Scale via Pathfinder handler

        :param port: Port of New Scale Pathfinder HTTP server
        :type port: int
        """
        super().__init__()

        self.num_axes = -1
        self.dimensions = [15, 15, 15]

        self.port = port

        # Test connection to New Scale HTTP server
        try:
            request.urlopen(f"http://localhost:{self.port}")
        except URLError:
            print(f"New Scale Pathfinder HTTP server not online on port {self.port}")
            print("Please start the HTTP server and try again.")
            input("Press Enter to exit...")
            exit(1)

    def query_data(self) -> dict:
        """Query New Scale HTTP server for data and return as dict.

        :return: Parsed JSON data from New Scale HTTP server.
        :rtype: dict
        """
        try:
            return json.loads(request.urlopen(f"http://localhost:{self.port}").read())
        except Exception as e:
            print(f"[ERROR]\t\t Unable to query for New Scale data: {type(e)} {e}\n")

    def query_manipulator_data(self, manipulator_id: str) -> dict:
        """Query New Scale HTTP server for data on a specific manipulator.

        :param manipulator_id: manipulator ID.
        :return: Parsed JSON data for a particular manipulator.
        :rtype: dict
        :raises ValueError: if manipulator ID is not found in query.
        """
        data_query = self.query_data()["ProbeArray"]
        manipulator_data = data_query[self.manipulators[manipulator_id]]

        # If the order of the manipulators switched (somehow)
        if manipulator_data["Id"] != manipulator_id:
            # Recalculate index and get data
            (manipulator_index, manipulator_data) = next(
                (
                    (index, data)
                    for index, data in enumerate(self.query_data()["ProbeArray"])
                    if data["Id"] == manipulator_id
                ),
                (None, None),
            )
            # Update index in manipulators dict
            if manipulator_index:
                self.manipulators[manipulator_id] = manipulator_index

        # If data query was unsuccessful
        if not manipulator_data:
            msg = f"Unable to find manipulator {manipulator_id}"
            raise ValueError(msg)

        # Return data
        return manipulator_data

    def _get_manipulators(self) -> list:
        return [probe["Id"] for probe in self.query_data()["ProbeArray"]]

    def _register_manipulator(self, manipulator_id: str) -> None:
        # Check if ID is a valid New Scale manipulator ID
        if manipulator_id not in self.VALID_MANIPULATOR_IDS:
            msg = f"Invalid manipulator ID {manipulator_id}"
            raise ValueError(msg)

        # Check if ID is connected
        if manipulator_id not in self._get_manipulators():
            msg = f"Manipulator {manipulator_id} not connected"
            raise ValueError(msg)

        # Get index of the manipulator
        manipulator_index = next(
            (index for index, data in enumerate(self.query_data()["ProbeArray"]) if data["Id"] == manipulator_id),
            None,
        )
        if manipulator_index is None:
            msg = f"Unable to find manipulator {manipulator_id}"
            raise ValueError(msg)
        self.manipulators[manipulator_id] = manipulator_index

    def _unregister_manipulator(self, manipulator_id: str) -> None:
        del self.manipulators[manipulator_id]

    def _get_pos(self, manipulator_id: str) -> PositionalResponse:
        """Get the current position of the manipulator in mm

        :param manipulator_id: manipulator ID
        :return: Callback parameters (position in (x, y, z, w) (or an empty array on
            error) in mm, error message)
        """
        manipulator_data = self.query_manipulator_data(manipulator_id)

        return PositionalResponse(
            position=Vector4(
                x=manipulator_data["Tip_X_ML"], y=manipulator_data["Tip_Y_AP"], z=manipulator_data["Tip_Z_DV"], w=0
            )
        )

    def _get_angles(self, manipulator_id: str) -> AngularResponse:
        manipulator_data = self.query_manipulator_data(manipulator_id)

        # Apply PosteriorAngle to Polar to get the correct angle.
        adjusted_polar = manipulator_data["Polar"] - self.query_data()["PosteriorAngle"]

        return AngularResponse(
            angles=Vector3(
                x=adjusted_polar if adjusted_polar > 0 else 360 + adjusted_polar,
                y=manipulator_data["Pitch"],
                z=manipulator_data.get("ShankOrientation", 0),
            )
        )

    def _get_shank_count(self, manipulator_id: str) -> ShankCountResponse:
        for probe in self.query_data()["ProbeArray"]:
            if probe["Id"] == manipulator_id:
                return ShankCountResponse(shank_count=probe.get("ShankCount", 1))

        return ShankCountResponse(error="Unable to find manipulator")

    async def _goto_pos(self, _: GotoPositionRequest) -> PositionalResponse:
        raise NotImplementedError

    async def _drive_to_depth(self, _: DriveToDepthRequest) -> DriveToDepthResponse:
        raise NotImplementedError

    def _set_inside_brain(self, _: InsideBrainRequest) -> BooleanStateResponse:
        raise NotImplementedError

    async def _calibrate(self, manipulator_id: str, sio: socketio.AsyncServer) -> str:
        raise NotImplementedError

    def _bypass_calibration(self, manipulator_id: str) -> str:
        return ""

    def _set_can_write(self, _: CanWriteRequest) -> BooleanStateResponse:
        raise NotImplementedError

    def _unified_space_to_platform_space(self, unified_position: list[float]) -> list[float]:
        raise NotImplementedError

    def _platform_space_to_unified_space(self, platform_position: list[float]) -> list[float]:
        raise NotImplementedError
