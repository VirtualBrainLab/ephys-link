"""Handle communications with Sensapex uMp API

Handles loading the Sensapex SDK and connecting to uMp devices. WebSocket events are
error checked and relayed to the
:class:`ephys_link.sensapex_manipulator.SensapexManipulator` class.

Function names here are the same as the WebSocket events. They are called when the
server receives an event from a client. In general, each function does the following:

1. Receive extracted arguments from :mod:`ephys_link.server`
2. Inside try/except block, call the appropriate Sensapex API function
3. Log/handle successes and failures
4. Return the callback parameters to :mod:`ephys_link.server`
"""

from pathlib import Path

import ephys_link.common as com
import ephys_link.platform_handler

from sensapex import UMP, UMError
from sensapex_manipulator import SensapexManipulator
# noinspection PyPackageRequirements
import socketio


class SensapexHandler(ephys_link.platform_handler.PlatformHandler):
    """Handler for Sensapex platform"""

    def __init__(self):
        super().__init__()
        self.ump = None

    def connect_to_ump(self) -> None:
        """Connect to uMp

        Only establish connection to Sensapex API when this function is called

        :return: None
        """
        UMP.set_library_path(
            str(Path(__file__).parent.parent.absolute()) + "/resources/")
        self.ump = UMP.get_ump()

    def _get_manipulators(self) -> list:
        if self.ump is None:
            raise ValueError("uMp not connected")
        return self.ump.list_devices()

    def _register_manipulator(self, manipulator_id: int) -> None:
        if self.ump is None:
            raise ValueError("uMp not connected")

        # noinspection PyUnresolvedReferences
        self.manipulators[manipulator_id] = SensapexManipulator(
            self.ump.get_device(manipulator_id)
        )

    def _unregister_manipulator(self, manipulator_id: int) -> None:
        del self.manipulators[manipulator_id]

    def _get_pos(self, manipulator_id: int) -> com.PositionalOutputData:
        return self.manipulators[manipulator_id].get_pos()

    async def _goto_pos(self,
                        manipulator_id: int, position: list[float], speed: int
                        ) -> com.PositionalOutputData:
        return await self.manipulators[manipulator_id].goto_pos(position, speed)

    async def _drive_to_depth(self,
                              manipulator_id: int, depth: float, speed: int
                              ) -> com.DriveToDepthOutputData:
        return await self.manipulators[manipulator_id].drive_to_depth(depth, speed)

    def _set_inside_brain(self, manipulator_id: int,
                          inside: bool) -> com.StateOutputData:
        self.manipulators[manipulator_id].set_inside_brain(inside)
        com.dprint(
            f"[SUCCESS]\t Set inside brain state for manipulator:"
            f" {manipulator_id}\n"
        )
        return com.StateOutputData(inside, "")

    async def _calibrate(self, manipulator_id: int, sio: socketio.AsyncServer) -> str:
        try:
            # Move manipulator to max position
            await self.manipulators[manipulator_id].goto_pos(
                [20000, 20000, 20000, 20000], 2000)

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

    def _bypass_calibration(self, manipulator_id: int) -> str:
        self.manipulators[manipulator_id].set_calibrated()
        com.dprint(
            f"[SUCCESS]\t Bypassed calibration for manipulator" f" {manipulator_id}\n"
        )
        return ""

    def _set_can_write(self,
                       manipulator_id: int, can_write: bool, hours: float,
                       sio: socketio.AsyncServer
                       ) -> com.StateOutputData:
        self.manipulators[manipulator_id].set_can_write(can_write, hours, sio)
        com.dprint(
            f"[SUCCESS]\t Set can_write state for manipulator" f" {manipulator_id}\n"
        )
        return com.StateOutputData(can_write, "")
