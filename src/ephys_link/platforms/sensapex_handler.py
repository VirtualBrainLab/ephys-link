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

    def _get_pos(self, manipulator_id: str) -> com.PositionalOutputData:
        return self.manipulators[manipulator_id].get_pos()

    def _get_angles(self, manipulator_id: str) -> com.AngularOutputData:
        raise NotImplementedError

    def _get_shank_count(self, manipulator_id: str) -> com.ShankCountOutputData:
        raise NotImplementedError

    async def _goto_pos(self, manipulator_id: str, position: list[float], speed: int) -> com.PositionalOutputData:
        return await self.manipulators[manipulator_id].goto_pos(position, speed)

    async def _drive_to_depth(self, manipulator_id: str, depth: float, speed: int) -> com.DriveToDepthOutputData:
        return await self.manipulators[manipulator_id].drive_to_depth(depth, speed)

    def _set_inside_brain(self, manipulator_id: str, inside: bool) -> com.StateOutputData:
        self.manipulators[manipulator_id].set_inside_brain(inside)
        com.dprint(f"[SUCCESS]\t Set inside brain state for manipulator:" f" {manipulator_id}\n")
        return com.StateOutputData(inside, "")

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

    def _set_can_write(
        self,
        manipulator_id: str,
        can_write: bool,
        hours: float,
        sio: socketio.AsyncServer,
    ) -> com.StateOutputData:
        self.manipulators[manipulator_id].set_can_write(can_write, hours, sio)
        com.dprint(f"[SUCCESS]\t Set can_write state for manipulator" f" {manipulator_id}\n")
        return com.StateOutputData(can_write, "")

    def _platform_space_to_unified_space(self, platform_position: list[float]) -> list[float]:
        # unified   <-  platform
        # +x        <-  +y
        # +y        <-  -z
        # +z        <-  +x
        # +d        <-  +d

        return [
            platform_position[1],
            self.dimensions[2] - platform_position[2],
            platform_position[0],
            platform_position[3],
        ]

    def _unified_space_to_platform_space(self, unified_position: list[float]) -> list[float]:
        # platform  <-  unified
        # +x        <-  +z
        # +y        <-  +x
        # +z        <-  -y
        # +d        <-  +d

        return [
            unified_position[2],
            unified_position[0],
            self.dimensions[2] - unified_position[1],
            unified_position[3],
        ]
