"""Handle communications with New Scale API

Implements New Scale specific API calls.

This is a subclass of :class:`ephys_link.platform_handler.PlatformHandler`.
"""

import importlib

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

        self.num_axes = 3
        self.dimensions = [15, 15, 15]

        # Load New Scale API
        # noinspection PyUnresolvedReferences
        clr.AddReference("ephys_link/resources/NstMotorCtrl")
        # noinspection PyUnresolvedReferences
        from NstMotorCtrl import NstCtrlHostIntf

        self.ctrl = NstCtrlHostIntf()

        # Connect manipulators and initialize
        self.ctrl.ShowProperties()
        self.ctrl.Initialize()

    def _get_manipulators(self) -> list:
        return list(map(str, range(self.ctrl.PortCount)))

    def _register_manipulator(self, manipulator_id: str) -> None:
        # Check if ID is numeric
        if not manipulator_id.isnumeric():
            raise ValueError("Manipulator ID must be numeric")

        # Check if ID is connected
        if manipulator_id not in self._get_manipulators():
            raise ValueError(f"Manipulator {manipulator_id} not connected")

        # Check if there are enough axes
        if int(manipulator_id) * 3 + 2 >= self.ctrl.AxisCount:
            raise ValueError(f"Manipulator {manipulator_id} has no axes")

        # Register manipulator
        first_axis_index = int(manipulator_id) * 3
        self.manipulators[manipulator_id] = importlib.import_module(
            "ephys_link.platforms.new_scale_manipulator"
        ).NewScaleManipulator(
            manipulator_id,
            self.ctrl.GetAxis(first_axis_index),
            self.ctrl.GetAxis(first_axis_index + 1),
            self.ctrl.GetAxis(first_axis_index + 2),
        )

    def _unregister_manipulator(self, manipulator_id: str) -> None:
        del self.manipulators[manipulator_id]

    def _get_pos(self, manipulator_id: str) -> com.PositionalOutputData:
        return self.manipulators[manipulator_id].get_pos()

    def _get_angles(self, manipulator_id: str) -> com.AngularOutputData:
        raise NotImplementedError

    async def _goto_pos(
        self, manipulator_id: str, position: list[float], speed: int
    ) -> com.PositionalOutputData:
        return await self.manipulators[manipulator_id].goto_pos(position, speed)

    async def _drive_to_depth(
        self, manipulator_id: str, depth: float, speed: int
    ) -> com.DriveToDepthOutputData:
        return await self.manipulators[manipulator_id].drive_to_depth(depth, speed)

    def _set_inside_brain(
        self, manipulator_id: str, inside: bool
    ) -> com.StateOutputData:
        self.manipulators[manipulator_id].set_inside_brain(inside)
        com.dprint(
            f"[SUCCESS]\t Set inside brain state for manipulator:"
            f" {manipulator_id}\n"
        )
        return com.StateOutputData(inside, "")

    async def _calibrate(self, manipulator_id: str, sio: socketio.AsyncServer) -> str:
        return (
            ""
            if self.manipulators[manipulator_id].calibrate()
            else "Error calling calibrate"
        )

    def _bypass_calibration(self, manipulator_id: str) -> str:
        self.manipulators[manipulator_id].set_calibrated()
        com.dprint(
            f"[SUCCESS]\t Bypassed calibration for manipulator" f" {manipulator_id}\n"
        )
        return ""

    def _set_can_write(
        self,
        manipulator_id: str,
        can_write: bool,
        hours: float,
        sio: socketio.AsyncServer,
    ) -> com.StateOutputData:
        self.manipulators[manipulator_id].set_can_write(can_write, hours, sio)
        com.dprint(
            f"[SUCCESS]\t Set can_write state for manipulator" f" {manipulator_id}\n"
        )
        return com.StateOutputData(can_write, "")

    def _platform_space_to_unified_space(
        self, platform_position: list[float]
    ) -> list[float]:
        # unified   <-  platform
        # +x        <-  -x
        # +y        <-  +z
        # +z        <-  +y
        # +d        <-  -d

        return [
            self.dimensions[0] - platform_position[0],
            platform_position[2],
            platform_position[1],
            self.dimensions[3] - platform_position[3],
        ]

    def _unified_space_to_platform_space(
        self, unified_position: list[float]
    ) -> list[float]:
        # platform  <-  unified
        # +x        <-  -x
        # +y        <-  +z
        # +z        <-  +y
        # +d        <-  -d

        return [
            self.dimensions[0] - unified_position[0],
            unified_position[2],
            unified_position[1],
            self.dimensions[3] - unified_position[3],
        ]
