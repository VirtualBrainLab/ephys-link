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

    def __init__(self, port: int = 8081):
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

    def _get_manipulators(self) -> list:
        return [probe['Id'] for probe in self.query_data()['ProbeArray']]

    def _register_manipulator(self, manipulator_id: int) -> None:
        pass

    def _unregister_manipulator(self, manipulator_id: int) -> None:
        pass

    def _get_pos(self, manipulator_id: int) -> com.PositionalOutputData:
        pass

    async def _goto_pos(self, manipulator_id: int, position: list[float],
                        speed: int) -> com.PositionalOutputData:
        pass

    async def _drive_to_depth(self, manipulator_id: int, depth: float,
                              speed: int) -> com.DriveToDepthOutputData:
        pass

    def _set_inside_brain(self, manipulator_id: int,
                          inside: bool) -> com.StateOutputData:
        pass

    async def _calibrate(self, manipulator_id: int, sio: socketio.AsyncServer) -> str:
        pass

    def _bypass_calibration(self, manipulator_id: int) -> str:
        pass

    def _set_can_write(self, manipulator_id: int, can_write: bool, hours: float,
                       sio: socketio.AsyncServer) -> com.StateOutputData:
        pass
