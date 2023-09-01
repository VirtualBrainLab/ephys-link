"""Handle communications with Sensapex uMp API

Implements Sensapex uMp specific API calls including coordinating the usage of the
:class:`ephys_link.platforms.sensapex_manipulator.SensapexManipulator` class.

This is a subclass of :class:`ephys_link.platform_handler.PlatformHandler`.
"""
from pathlib import Path

# noinspection PyPackageRequirements
import socketio
from sensapex import UMP, UMError
from sensapex_manipulator import SensapexManipulator

import src.ephys_link.common as com
from src.ephys_link.platform_handler import PlatformHandler


class SensapexHandler(PlatformHandler):
    """Handler for Sensapex platform"""

    def __init__(self):
        super().__init__()

        # Establish connection to Sensapex API (exit if connection fails)
        UMP.set_library_path(
            str(Path(__file__).parent.parent.absolute()) + "/resources/"
        )
        self.ump = UMP.get_ump()
        if self.ump is None:
            raise ValueError("Unable to connect to uMp")

    def _get_manipulators(self) -> list:
        return list(map(str, self.ump.list_devices()))

    def _register_manipulator(self, manipulator_id: str) -> None:
        if not manipulator_id.isnumeric():
            raise ValueError("Manipulator ID must be numeric")

        self.manipulators[manipulator_id] = SensapexManipulator(
            self.ump.get_device(int(manipulator_id))
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
        try:
            # Move manipulator to max position
            await self.manipulators[manipulator_id].goto_pos(
                [20000, 20000, 20000, 20000], 2000
            )

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
            return ""
        except UMError as e:
            # SDK call error
            print(f"[ERROR]\t\t Calling calibrate manipulator {manipulator_id}")
            print(f"{e}\n")
            return "Error calling calibrate"

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
