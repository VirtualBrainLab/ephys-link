"""Handle communications with Sensapex uMp API

This supports the uMp-4 manipulator. Any Sensapex variants should extend this class.

Implements Sensapex uMp specific API calls including coordinating the usage of the
:class:`ephys_link.platforms.sensapex_manipulator.SensapexManipulator` class.

This is a subclass of :class:`ephys_link.platform_handler.PlatformHandler`.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from sensapex import UMP, UMError
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

import ephys_link.common as com
from ephys_link.platform_handler import PlatformHandler
from ephys_link.platforms.sensapex_manipulator import SensapexManipulator

if TYPE_CHECKING:
    import socketio


class SensapexHandler(PlatformHandler):
    """Handler for Sensapex platform."""

    def __init__(self) -> None:
        super().__init__()

        # Establish connection to Sensapex API (exit if connection fails)
        UMP.set_library_path(str(Path(__file__).parent.parent.absolute()) + "/resources/")
        self.ump = UMP.get_ump()
        if self.ump is None:
            msg = "Unable to connect to uMp"
            raise ValueError(msg)

    def _get_manipulators(self) -> list:
        return list(map(str, self.ump.list_devices()))

    def _register_manipulator(self, manipulator_id: str) -> None:
        if not manipulator_id.isnumeric():
            msg = "Manipulator ID must be numeric"
            raise ValueError(msg)

        self.manipulators[manipulator_id] = SensapexManipulator(self.ump.get_device(int(manipulator_id)))

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
        try:
            # Move manipulator to max position
            await self.manipulators[manipulator_id].goto_pos([20000, 20000, 20000, 20000], 2000)

            # Call calibrate
            self.manipulators[manipulator_id].call_calibrate()

            # Wait for calibration to complete
            still_working = True
            while still_working:
                cur_pos = self.manipulators[manipulator_id].get_pos()["position"]

                # Check difference between current and target position
                for prev, cur in zip([10000, 10000, 10000, 10000], cur_pos):
                    if abs(prev - cur) > 1:
                        still_working = True
                        break
                    still_working = False

                # Sleep for a bit
                await sio.sleep(0.5)

            # Calibration complete
            self.manipulators[manipulator_id].set_calibrated()
            com.dprint(f"[SUCCESS]\t Calibrated manipulator {manipulator_id}\n")
        except UMError as e:
            # SDK call error
            print(f"[ERROR]\t\t Calling calibrate manipulator {manipulator_id}")
            print(f"{e}\n")
            return "Error calling calibrate"
        else:
            return ""

    def _bypass_calibration(self, manipulator_id: str) -> str:
        self.manipulators[manipulator_id].set_calibrated()
        com.dprint(f"[SUCCESS]\t Bypassed calibration for manipulator" f" {manipulator_id}\n")
        return ""

    def _set_can_write(self, request: CanWriteRequest) -> BooleanStateResponse:
        self.manipulators[request.manipulator_id].set_can_write(request)
        com.dprint(f"[SUCCESS]\t Set can_write state for manipulator {request.manipulator_id}\n")
        return BooleanStateResponse(state=request.can_write)

    def _platform_space_to_unified_space(self, platform_position: Vector4) -> Vector4:
        # unified   <-  platform
        # +x        <-  +y
        # +y        <-  -z
        # +z        <-  +x
        # +d        <-  +d

        return Vector4(
            x=platform_position.y,
            y=self.dimensions.z - platform_position.z,
            z=platform_position.x,
            w=platform_position.w,
        )

    def _unified_space_to_platform_space(self, unified_position: Vector4) -> Vector4:
        # platform  <-  unified
        # +x        <-  +z
        # +y        <-  +x
        # +z        <-  -y
        # +d        <-  +d

        return Vector4(
            x=unified_position.z, y=unified_position.x, z=self.dimensions.z - unified_position.y, w=unified_position.w
        )
