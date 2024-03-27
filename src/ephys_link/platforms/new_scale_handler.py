"""Handle communications with New Scale API

Implements New Scale specific API calls.

This is a subclass of :class:`ephys_link.platform_handler.PlatformHandler`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

# noinspection PyUnresolvedReferences
from NstMotorCtrl import NstCtrlHostIntf
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
from vbl_aquarium.models.unity import Vector4

from ephys_link import common as com
from ephys_link.platform_handler import PlatformHandler
from ephys_link.platforms.new_scale_manipulator import NewScaleManipulator

if TYPE_CHECKING:
    import socketio


class NewScaleHandler(PlatformHandler):
    """Handler for New Scale platform"""

    def __init__(self) -> None:
        """Initialize New Scale handler"""
        super().__init__()

        self.num_axes = 3
        self.dimensions = Vector4(x=20, y=20, z=20, w=0)

        self.ctrl = NstCtrlHostIntf()

        # Connect manipulators and initialize
        self.ctrl.ShowProperties()
        self.ctrl.Initialize()

    def _get_manipulators(self) -> list:
        return list(map(str, range(self.ctrl.PortCount)))

    def _register_manipulator(self, manipulator_id: str) -> None:
        # Check if ID is numeric
        if not manipulator_id.isnumeric():
            msg = "Manipulator ID must be numeric"
            raise ValueError(msg)

        # Check if ID is connected
        if manipulator_id not in self._get_manipulators():
            msg = f"Manipulator {manipulator_id} not connected"
            raise ValueError(msg)

        # Check if there are enough axes
        if int(manipulator_id) * 3 + 2 >= self.ctrl.AxisCount:
            msg = f"Manipulator {manipulator_id} has no axes"
            raise ValueError(msg)

        # Register manipulator
        first_axis_index = int(manipulator_id) * 3
        self.manipulators[manipulator_id] = NewScaleManipulator(
            manipulator_id,
            self.ctrl.GetAxis(first_axis_index),
            self.ctrl.GetAxis(first_axis_index + 1),
            self.ctrl.GetAxis(first_axis_index + 2),
        )

    def _unregister_manipulator(self, manipulator_id: str) -> None:
        del self.manipulators[manipulator_id]

    def _get_pos(self, manipulator_id: str) -> PositionalResponse:
        return self.manipulators[manipulator_id].get_pos()

    def _get_angles(self, manipulator_id: str) -> AngularResponse:
        raise NotImplementedError

    def _get_shank_count(self, manipulator_id: str) -> ShankCountResponse:
        raise NotImplementedError

    async def _goto_pos(self, request: GotoPositionRequest) -> PositionalResponse:
        return await self.manipulators[request.manipulator_id].goto_pos(request)

    async def _drive_to_depth(self, request: DriveToDepthRequest) -> DriveToDepthResponse:
        return await self.manipulators[request.manipulator_id].drive_to_depth(request)

    def _set_inside_brain(self, request: InsideBrainRequest) -> BooleanStateResponse:
        self.manipulators[request.manipulator_id].set_inside_brain(request.inside)
        com.dprint(f"[SUCCESS]\t Set inside brain state for manipulator: {request.manipulator_id}\n")
        return BooleanStateResponse(state=request.inside)

    async def _calibrate(self, manipulator_id: str, sio: socketio.AsyncServer) -> str:
        return "" if self.manipulators[manipulator_id].calibrate() else "Error calling calibrate"

    def _bypass_calibration(self, manipulator_id: str) -> str:
        self.manipulators[manipulator_id].set_calibrated()
        com.dprint(f"[SUCCESS]\t Bypassed calibration for manipulator" f" {manipulator_id}\n")
        return ""

    def _set_can_write(self, request: CanWriteRequest) -> BooleanStateResponse:
        self.manipulators[request.manipulator_id].set_can_write(request)
        com.dprint(f"[SUCCESS]\t Set can_write state for manipulator {request.manipulator_id}\n")
        return BooleanStateResponse(state=request.can_write)

    def _platform_space_to_unified_space(self, platform_position: list[float]) -> list[float]:
        # unified   <-  platform
        # +x        <-  -x
        # +y        <-  +z
        # +z        <-  +y
        # +d        <-  -d

        return [
            self.dimensions[0] - platform_position[0],
            platform_position[2],
            platform_position[1],
            self.dimensions[2] - platform_position[3],
        ]

    def _unified_space_to_platform_space(self, unified_position: list[float]) -> list[float]:
        # platform  <-  unified
        # +x        <-  -x
        # +y        <-  +z
        # +z        <-  +y
        # +d        <-  -d

        return [
            self.dimensions[0] - unified_position[0],
            unified_position[2],
            unified_position[1],
            self.dimensions[2] - unified_position[3],
        ]
