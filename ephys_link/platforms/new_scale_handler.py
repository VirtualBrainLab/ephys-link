"""Handle communications with New Scale API

Implements New Scale specific API calls.

This is a subclass of :class:`ephys_link.platform_handler.PlatformHandler`.
"""

from ephys_link import common as com
from ephys_link.platform_handler import PlatformHandler

from urllib import request
from json import loads

# noinspection PyPackageRequirements
import socketio


class NewScaleHandler(PlatformHandler):
    """Handler for New Scale platform"""

    # Valid New Scale manipulator IDs
    VALID_MANIPULATOR_IDS = {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K",
                             "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
                             "W", "X", "Y", "Z", "AA", "AB", "AC", "AD", "AE", "AF",
                             "AG", "AH", "AI", "AJ", "AK", "AL", "AM", "AN"}

    def __init__(self, port: int = 8080):
        super().__init__()
        self.port = port

        # Test connection to New Scale HTTP server
        try:
            request.urlopen(f"http://localhost:{self.port}")
        except Exception as e:
            raise ValueError(
                f"New Scale HTTP server not online on port {self.port}") from e

    def query_data(self) -> dict:
        """Query New Scale HTTP server for data and return as dict

        :return: dict of data (originally in JSON)
        """
        try:
            raw_data = request.urlopen(f"http://localhost:{self.port}").read()
            return loads(raw_data)
        except Exception as e:
            print(f"[ERROR]\t\t Unable to query for New Scale data: {type(e)} {e}\n")

    def query_manipulator_data(self, manipulator_id: str) -> dict:
        """Query New Scale HTTP server for data on a specific manipulator

        :param manipulator_id: manipulator ID
        :return: dict of data (originally in JSON)
        :raises ValueError: if manipulator ID is not found in query
        """
        data = next(
            (manipulator for manipulator in self.query_data()['ProbeArray'] if
             manipulator['Id'] == manipulator_id), None)
        if not data:
            raise ValueError(f"Unable to find manipulator {manipulator_id}")
        return data

    def _get_manipulators(self) -> list:
        return [probe['Id'] for probe in self.query_data()['ProbeArray']]

    def _register_manipulator(self, manipulator_id: str) -> None:
        # Check if ID is a valid New Scale manipulator ID
        if manipulator_id not in self.VALID_MANIPULATOR_IDS:
            raise ValueError(f"Invalid manipulator ID {manipulator_id}")

        # Check if ID is connected
        if manipulator_id not in self._get_manipulators():
            raise ValueError(f"Manipulator {manipulator_id} not connected")

        manipulator_data = self.query_manipulator_data(manipulator_id)
        self.manipulators[manipulator_id] = manipulator_data['SerialNumber']

    def _unregister_manipulator(self, manipulator_id: str) -> None:
        del self.manipulators[manipulator_id]

    def _get_pos(self, manipulator_id: str) -> com.PositionalOutputData:
        manipulator_data = self.query_manipulator_data(manipulator_id)
        return com.PositionalOutputData(
            [manipulator_data['Stage_X'], manipulator_data['Stage_Y'],
             manipulator_data['Stage_Z'], 0], "")

    async def _goto_pos(self, manipulator_id: str, position: list[float],
                        speed: int) -> com.PositionalOutputData:
        pass

    async def _drive_to_depth(self, manipulator_id: str, depth: float,
                              speed: int) -> com.DriveToDepthOutputData:
        pass

    def _set_inside_brain(self, manipulator_id: str,
                          inside: bool) -> com.StateOutputData:
        pass

    async def _calibrate(self, manipulator_id: str, sio: socketio.AsyncServer) -> str:
        pass

    def _bypass_calibration(self, manipulator_id: str) -> str:
        pass

    def _set_can_write(self, manipulator_id: str, can_write: bool, hours: float,
                       sio: socketio.AsyncServer) -> com.StateOutputData:
        pass
