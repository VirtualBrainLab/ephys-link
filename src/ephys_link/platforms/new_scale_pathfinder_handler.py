"""Handle communications with New Scale's HTTP server

Implements New Scale specific API calls.

This is a subclass of :class:`ephys_link.platform_handler.PlatformHandler`.
"""

from __future__ import annotations

from json import loads
from typing import TYPE_CHECKING
from urllib import request

from ephys_link import common as com
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
        except Exception as e:
            msg = f"New Scale HTTP server not online on port {self.port}"
            raise ValueError(msg) from e

    def query_data(self) -> dict:
        """Query New Scale HTTP server for data and return as dict

        :return: dict of data (originally in JSON)
        """
        try:
            return loads(request.urlopen(f"http://localhost:{self.port}").read())
        except Exception as e:
            print(f"[ERROR]\t\t Unable to query for New Scale data: {type(e)} {e}\n")

    def query_manipulator_data(self, manipulator_id: str) -> dict:
        """Query New Scale HTTP server for data on a specific manipulator

        :param manipulator_id: manipulator ID
        :return: dict of data (originally in JSON)
        :raises ValueError: if manipulator ID is not found in query
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

    def _get_pos(self, manipulator_id: str) -> com.PositionalOutputData:
        """Get the current position of the manipulator in mm

        :param manipulator_id: manipulator ID
        :return: Callback parameters (position in (x, y, z, w) (or an empty array on
            error) in mm, error message)
        """
        manipulator_data = self.query_manipulator_data(manipulator_id)

        return com.PositionalOutputData(
            [
                manipulator_data["Tip_X_ML"],
                manipulator_data["Tip_Y_AP"],
                manipulator_data["Tip_Z_DV"],
                0,
            ],
            "",
        )

    def _get_angles(self, manipulator_id: str) -> com.AngularOutputData:
        """Get the current angles of the manipulator in degrees

        :param manipulator_id: manipulator ID
        :return: Callback parameters (angles in (yaw, pitch, roll) (or an empty array on
            error) in degrees, error message)
        """
        manipulator_data = self.query_manipulator_data(manipulator_id)

        return com.AngularOutputData(
            [
                manipulator_data["Polar"],
                manipulator_data["Pitch"],
                manipulator_data["Roll"],
            ],
            "",
        )

    def _get_shank_count(self, manipulator_id: str) -> com.ShankCountOutputData:
        """Get the number of shanks on the probe

        :param manipulator_id: manipulator ID
        :return: Callback parameters (number of shanks (or -1 on error), error message)
        """
        for probe in self.query_data()["ProbeArray"]:
            if probe["Id"] == manipulator_id:
                return com.ShankCountOutputData(probe["ShankCount"], "")

        return com.ShankCountOutputData(-1, "Unable to find manipulator")

    async def _goto_pos(self, manipulator_id: str, position: list[float], speed: int) -> com.PositionalOutputData:
        pass

    async def _drive_to_depth(self, manipulator_id: str, depth: float, speed: int) -> com.DriveToDepthOutputData:
        pass

    def _set_inside_brain(self, manipulator_id: str, inside: bool) -> com.StateOutputData:
        pass

    async def _calibrate(self, manipulator_id: str, sio: socketio.AsyncServer) -> str:
        pass

    def _bypass_calibration(self, manipulator_id: str) -> str:
        return ""

    def _set_can_write(
        self,
        manipulator_id: str,
        can_write: bool,
        hours: float,
        sio: socketio.AsyncServer,
    ) -> com.StateOutputData:
        pass

    def _unified_space_to_platform_space(self, unified_position: list[float]) -> list[float]:
        pass

    def _platform_space_to_unified_space(self, platform_position: list[float]) -> list[float]:
        pass
