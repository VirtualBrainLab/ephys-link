"""Handle communications with New Scale API

Implements New Scale specific API calls.

This is a subclass of :class:`ephys_link.platform_handler.PlatformHandler`.
"""

# noinspection PyPackageRequirements
import clr

# noinspection PyPackageRequirements
import socketio

from ephys_link import common as com
from ephys_link.platform_handler import PlatformHandler


class NewScaleHandler(PlatformHandler):
    """Handler for New Scale platform"""

    def __init__(self) -> None:
        """Initialize New Scale handler"""
        super().__init__()

        # Load New Scale API
        clr.AddReference("../resources/NstMotorCtrl")
        # noinspection PyUnresolvedReferences
        from NstMotorCtrl import NstCtrlHostIntf
        self.ctrl = NstCtrlHostIntf()

        # Connect manipulators and initialize
        self.ctrl.ShowProperties()
        self.ctrl.Initialize()

        # Create manipulator objects
        self.manipulators = {}
        from new_scale_manipulator import NewScaleManipulator
        axis_index = 0

        for i in range(self.ctrl.PortCount):
            self.manipulators[i] = NewScaleManipulator(str(i), self.ctrl.GetAxis(axis_index),
                                                       self.ctrl.GetAxis(axis_index + 1),
                                                       self.ctrl.GetAxis(axis_index + 2))
            axis_index += 3

    def _get_manipulators(self) -> list:
        return list(self.manipulators.keys())

    def _register_manipulator(self, manipulator_id: str) -> None:
        # Check if ID is a valid New Scale manipulator ID
        if manipulator_id not in self.VALID_MANIPULATOR_IDS:
            raise ValueError(f"Invalid manipulator ID {manipulator_id}")

        # Check if ID is connected
        if manipulator_id not in self._get_manipulators():
            raise ValueError(f"Manipulator {manipulator_id} not connected")

        # Get index of the manipulator
        manipulator_index = next(
            (
                index
                for index, data in enumerate(self.query_data()["ProbeArray"])
                if data["Id"] == manipulator_id
            ),
            None,
        )
        if manipulator_index is None:
            raise ValueError(f"Unable to find manipulator {manipulator_id}")
        self.manipulators[manipulator_id] = manipulator_index

    def _unregister_manipulator(self, manipulator_id: str) -> None:
        del self.manipulators[manipulator_id]

    def _get_pos(self, manipulator_id: str) -> com.PositionalOutputData:
        manipulator_data = self.query_manipulator_data(manipulator_id)
        return com.PositionalOutputData(
            [
                manipulator_data["Stage_X"],
                manipulator_data["Stage_Y"],
                manipulator_data["Stage_Z"],
                0,
            ],
            "",
        )

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
        return ""

    def _set_can_write(
            self,
            manipulator_id: str,
            can_write: bool,
            hours: float,
            sio: socketio.AsyncServer,
    ) -> com.StateOutputData:
        pass
