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

    def get_manipulators(self) -> com.GetManipulatorsOutputData:
        if self.ump is None:
            raise ValueError("uMp not connected")

        devices = []
        error = "Error getting manipulators"

        try:
            # noinspection PyUnresolvedReferences
            devices = self.ump.list_devices()
            error = ""
        except Exception as e:
            print(f"[ERROR]\t\t Getting manipulators: {e}\n")
        finally:
            return com.GetManipulatorsOutputData(devices, error)

    def register_manipulator(self, manipulator_id: int) -> str:
        if self.ump is None:
            raise ValueError("uMp not connected")

        # Check if manipulator is already registered
        if manipulator_id in self.manipulators:
            print(
                f"[ERROR]\t\t Manipulator already registered:" f" {manipulator_id}\n")
            return "Manipulator already registered"

        try:
            # Register manipulator
            # noinspection PyUnresolvedReferences
            self.manipulators[manipulator_id] = SensapexManipulator(
                ump.get_device(manipulator_id)
            )

            com.dprint(f"[SUCCESS]\t Registered manipulator: {manipulator_id}\n")
            return ""

        except ValueError:
            # Manipulator not found in UMP
            print(f"[ERROR]\t\t Manipulator not found: {manipulator_id}\n")
            return "Manipulator not found"

        except Exception as e:
            # Other error
            print(f"[ERROR]\t\t Registering manipulator: {manipulator_id}")
            print(f"{e}\n")
            return "Error registering manipulator"

    def unregister_manipulator(self, manipulator_id: int) -> str:
        # Check if manipulator is not registered
        if manipulator_id not in self.manipulators:
            print(f"[ERROR]\t\t Manipulator not registered: {manipulator_id}\n")
            return "Manipulator not registered"

        try:
            # Unregister manipulator
            del self.manipulators[manipulator_id]

            com.dprint(f"[SUCCESS]\t Unregistered manipulator: {manipulator_id}\n")
            return ""
        except Exception as e:
            # Other error
            print(f"[ERROR]\t\t Unregistering manipulator: {manipulator_id}")
            print(f"{e}\n")
            return "Error unregistering manipulator"

    def get_pos(self, manipulator_id: int) -> com.PositionalOutputData:
        try:
            # Check calibration status
            if not self.manipulators[manipulator_id].get_calibrated():
                print(f"[ERROR]\t\t Calibration not complete: {manipulator_id}\n")
                return com.PositionalOutputData([], "Manipulator not calibrated")

            # Get position
            return self.manipulators[manipulator_id].get_pos()

        except KeyError:
            # Manipulator not found in registered manipulators
            print(f"[ERROR]\t\t Manipulator not registered: {manipulator_id}")
            return com.PositionalOutputData([], "Manipulator not registered")

    async def goto_pos(self,
                       manipulator_id: int, position: list[float], speed: int
                       ) -> com.PositionalOutputData:
        try:
            # Check calibration status
            if not self.manipulators[manipulator_id].get_calibrated():
                print(f"[ERROR]\t\t Calibration not complete: {manipulator_id}\n")
                return com.PositionalOutputData([], "Manipulator not calibrated")

            # Check write state
            if not self.manipulators[manipulator_id].get_can_write():
                print(f"[ERROR]\t\t Cannot write to manipulator: {manipulator_id}")
                return com.PositionalOutputData([], "Cannot write to manipulator")

            return await self.manipulators[manipulator_id].goto_pos(position, speed)

        except KeyError:
            # Manipulator not found in registered manipulators
            print(f"[ERROR]\t\t Manipulator not registered: {manipulator_id}\n")
            return com.PositionalOutputData([], "Manipulator not registered")

    async def drive_to_depth(self,
                             manipulator_id: int, depth: float, speed: int
                             ) -> com.DriveToDepthOutputData:
        try:
            # Check calibration status
            if not self.manipulators[manipulator_id].get_calibrated():
                print(f"[ERROR]\t\t Calibration not complete: {manipulator_id}\n")
                return com.DriveToDepthOutputData(0, "Manipulator not calibrated")

            # Check write state
            if not self.manipulators[manipulator_id].get_can_write():
                print(f"[ERROR]\t\t Cannot write to manipulator: {manipulator_id}")
                return com.DriveToDepthOutputData(0, "Cannot write to manipulator")

            return await self.manipulators[manipulator_id].drive_to_depth(depth, speed)

        except KeyError:
            # Manipulator not found in registered manipulators
            print(f"[ERROR]\t\t Manipulator not registered: {manipulator_id}\n")
            return com.DriveToDepthOutputData(0, "Manipulator " "not registered")

    def set_inside_brain(self, manipulator_id: int,
                         inside: bool) -> com.StateOutputData:
        try:
            # Check calibration status
            if not self.manipulators[manipulator_id].get_calibrated():
                print("[ERROR]\t\t Calibration not complete\n")
                return com.StateOutputData(False, "Manipulator not calibrated")

            self.manipulators[manipulator_id].set_inside_brain(inside)
            com.dprint(
                f"[SUCCESS]\t Set inside brain state for manipulator:"
                f" {manipulator_id}\n"
            )
            return com.StateOutputData(inside, "")
        except KeyError:
            # Manipulator not found in registered manipulators
            print(f"[ERROR]\t\t Manipulator {manipulator_id} not registered\n")
            return com.StateOutputData(False, "Manipulator not " "registered")

        except Exception as e:
            # Other error
            print(
                f"[ERROR]\t\t Set manipulator {manipulator_id} inside brain " f"state")
            print(f"{e}\n")
            return com.StateOutputData(False, "Error setting " "inside brain")

    async def calibrate(self, manipulator_id: int, sio: socketio.AsyncServer) -> str:
        try:
            # Check write state
            if not self.manipulators[manipulator_id].get_can_write():
                print(f"[ERROR]\t\t Cannot write to manipulator: {manipulator_id}")
                return "Cannot write to manipulator"

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

        except KeyError:
            # Manipulator not found in registered manipulators
            print(f"[ERROR]\t\t Manipulator {manipulator_id} not registered\n")
            return "Manipulator not registered"

        except UMError as e:
            # SDK call error
            print(f"[ERROR]\t\t Calling calibrate manipulator {manipulator_id}")
            print(f"{e}\n")
            return "Error calling calibrate"

        except Exception as e:
            # Other error
            print(f"[ERROR]\t\t Calibrate manipulator {manipulator_id}")
            print(f"{e}\n")
            return "Error calibrating manipulator"

    def bypass_calibration(self, manipulator_id: int) -> str:
        try:
            # Bypass calibration
            self.manipulators[manipulator_id].set_calibrated()
            com.dprint(
                f"[SUCCESS]\t Bypassed calibration for manipulator" f" {manipulator_id}\n"
            )
            return ""

        except KeyError:
            # Manipulator not found in registered manipulators
            print(f"[ERROR]\t\t Manipulator {manipulator_id} not registered\n")
            return "Manipulator not registered"

        except Exception as e:
            # Other error
            print(f"[ERROR]\t\t Bypass calibration of manipulator {manipulator_id}")
            print(f"{e}\n")
            return "Error bypassing calibration"

    def set_can_write(self,
                      manipulator_id: int, can_write: bool, hours: float,
                      sio: socketio.AsyncServer
                      ) -> com.StateOutputData:
        try:
            self.manipulators[manipulator_id].set_can_write(can_write, hours, sio)
            com.dprint(
                f"[SUCCESS]\t Set can_write state for manipulator" f" {manipulator_id}\n"
            )
            return com.StateOutputData(can_write, "")

        except KeyError:
            # Manipulator not found in registered manipulators
            print(f"[ERROR]\t\t Manipulator not registered: {manipulator_id}\n")
            return com.StateOutputData(False, "Manipulator not " "registered")

        except Exception as e:
            # Other error
            print(f"[ERROR]\t\t Set manipulator {manipulator_id} can_write state")
            print(f"{e}\n")
            return com.StateOutputData(False, "Error setting " "can_write")
