from pathlib import Path

import socketio
from sensapex import UMP

from ephys_link import common as com
from ephys_link.platform_handler import PlatformHandler


class UMP3Handler(PlatformHandler):
    def __init__(self):
        super().__init__()

        self.num_axes = 3
        self.dimensions = [20, 20, 20]

        # Establish connection to Sensapex API (exit if connection fails)
        UMP.set_library_path(
            str(Path(__file__).parent.parent.absolute()) + "/resources/"
        )
        self.ump = UMP.get_ump()
        if self.ump is None:
            raise ValueError("Unable to connect to uMp")

    def _get_manipulators(self) -> list:
        pass

    def _register_manipulator(self, manipulator_id: str) -> None:
        pass

    def _unregister_manipulator(self, manipulator_id: str) -> None:
        pass

    def _get_pos(self, manipulator_id: str) -> com.PositionalOutputData:
        pass

    def _get_angles(self, manipulator_id: str) -> com.AngularOutputData:
        pass

    async def _goto_pos(
        self, manipulator_id: str, position: list[float], speed: int
    ) -> com.PositionalOutputData:
        pass

    async def _drive_to_depth(
        self, manipulator_id: str, depth: float, speed: int
    ) -> com.DriveToDepthOutputData:
        pass

    def _set_inside_brain(
        self, manipulator_id: str, inside: bool
    ) -> com.StateOutputData:
        pass

    async def _calibrate(self, manipulator_id: str, sio: socketio.AsyncServer) -> str:
        pass

    def _bypass_calibration(self, manipulator_id: str) -> str:
        pass

    def _set_can_write(
        self,
        manipulator_id: str,
        can_write: bool,
        hours: float,
        sio: socketio.AsyncServer,
    ) -> com.StateOutputData:
        pass

    def _platform_space_to_unified_space(
        self, platform_position: list[float]
    ) -> list[float]:
        pass

    def _unified_space_to_platform_space(
        self, unified_position: list[float]
    ) -> list[float]:
        pass
