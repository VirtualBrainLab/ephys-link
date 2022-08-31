"""Handling communications with Sensapex manipulators and the uMp API

Handles loading the Sensapex SDK and connecting to uMp devices. WebSocket events are
error checked and relayed to events to the :class:`Manipulator` class.
"""
import time
from pathlib import Path

# noinspection PyPackageRequirements
import socketio

import common as com
from sensapex_manipulator import SensapexManipulator
from sensapex import UMP, UMError
from serial import Serial
from serial.tools.list_ports import comports

# Registered manipulators
manipulators = {}

# Setup Sensapex
UMP.set_library_path(str(Path(__file__).parent.absolute()) + "/resources/")
ump = UMP.get_ump()

# Setup Arduino serial port
poll_rate = 0.05
continue_polling = True


def poll_serial(serial_port: str) -> None:
    """Continuously poll serial port for data

    :param serial_port: The serial port to poll
    :type serial_port: str
    :return: None
    :rtype: None
    """
    target_port = serial_port
    if serial_port is None:
        # Search for serial ports
        for port, desc, _ in comports():
            if "USB Serial Device" in desc:
                target_port = port
                break
    elif serial_port == "no-e-stop":
        # Stop polling if no-e-stop is specified
        return None

    ser = Serial(target_port, 9600, timeout=poll_rate)
    while continue_polling:
        if ser.in_waiting > 0:
            ser.readline()
            # Cause a break
            com.dprint("STOPPING EVERYTHING")
            stop()
            ser.reset_input_buffer()
        time.sleep(poll_rate)
    ser.close()


# Event handlers
def reset() -> bool:
    """Reset handler

    :return: True if successful, False otherwise
    :rtype: bool
    """
    stop_result = stop()
    manipulators.clear()
    return stop_result


def stop() -> bool:
    """Stop handler

    :return: True if successful, False otherwise
    :rtype: bool
    """
    try:
        for manipulator in manipulators.values():
            manipulator.stop()
        return True
    except Exception as e:
        print(f"[ERROR]\t\t Stopping manipulators: {e}\n")
        return False


def get_manipulators() -> com.GetManipulatorsOutputData:
    """Get all registered manipulators

    :return: Callback parameters (manipulators, error)
    :rtype: :class:`common.GetManipulatorsOutputData`
    """
    devices = []
    error = "Error getting manipulators"

    try:
        devices = ump.list_devices()
        error = ""
    except Exception as e:
        print(f"[ERROR]\t\t Getting manipulators: {e}\n")
    finally:
        return com.GetManipulatorsOutputData(devices, error)


def register_manipulator(manipulator_id: int) -> str:
    """Register a manipulator

    :param manipulator_id: The ID of the manipulator to register.
    :type manipulator_id: int
    :return: Callback parameter (Error message (on error))
    :rtype: str
    """
    # Check if manipulator is already registered
    if manipulator_id in manipulators:
        print(f"[ERROR]\t\t Manipulator already registered:" f" {manipulator_id}\n")
        return "Manipulator already registered"

    try:
        # Register manipulator
        manipulators[manipulator_id] = SensapexManipulator(
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


def unregister_manipulator(manipulator_id: int) -> str:
    """Unregister a manipulator

    :param manipulator_id: The ID of the manipulator to unregister.
    :type manipulator_id: int
    :return: Callback parameters (error message (on error))

    """
    # Check if manipulator is not registered
    if manipulator_id not in manipulators:
        print(f"[ERROR]\t\t Manipulator not registered: {manipulator_id}\n")
        return "Manipulator not registered"

    try:
        # Unregister manipulator
        del manipulators[manipulator_id]

        com.dprint(f"[SUCCESS]\t Unregistered manipulator: {manipulator_id}\n")
        return ""
    except Exception as e:
        # Other error
        print(f"[ERROR]\t\t Unregistering manipulator: {manipulator_id}")
        print(f"{e}\n")
        return "Error unregistering manipulator"


def get_pos(manipulator_id: int) -> com.PositionalOutputData:
    """Get the current position of a manipulator

    :param manipulator_id: The ID of the manipulator to get the position of.
    :type manipulator_id: int
    :return: Callback parameters (manipulator ID, position in (x, y, z,
    w) (or an empty array on error), error message)
    :rtype: :class:`common.PositionalOutputData`
    """
    try:
        # Check calibration status
        if not manipulators[manipulator_id].get_calibrated():
            print(f"[ERROR]\t\t Calibration not complete: {manipulator_id}\n")
            return com.PositionalOutputData([], "Manipulator not calibrated")

        # Get position
        return manipulators[manipulator_id].get_pos()

    except KeyError:
        # Manipulator not found in registered manipulators
        print(f"[ERROR]\t\t Manipulator not registered: {manipulator_id}")
        return com.PositionalOutputData([], "Manipulator not registered")


async def goto_pos(
    manipulator_id: int, position: list[float], speed: int
) -> com.PositionalOutputData:
    """Move manipulator to position

    :param manipulator_id: The ID of the manipulator to move
    :type manipulator_id: int
    :param position: The position to move to
    :type position: list[float]
    :param speed: The speed to move at (in µm/s)
    :type speed: int
    :return: Callback parameters (manipulator ID, position in (x, y, z,
    w) (or an empty array on error), error message)
    :rtype: :class:`common.PositionalOutputData`
    """
    try:
        # Check calibration status
        if not manipulators[manipulator_id].get_calibrated():
            print(f"[ERROR]\t\t Calibration not complete: {manipulator_id}\n")
            return com.PositionalOutputData([], "Manipulator not calibrated")

        # Check write state
        if not manipulators[manipulator_id].get_can_write():
            print(f"[ERROR]\t\t Cannot write to manipulator: {manipulator_id}")
            return com.PositionalOutputData([], "Cannot write to manipulator")

        return await manipulators[manipulator_id].goto_pos(position, speed)

    except KeyError:
        # Manipulator not found in registered manipulators
        print(f"[ERROR]\t\t Manipulator not registered: {manipulator_id}\n")
        return com.PositionalOutputData([], "Manipulator not registered")


async def drive_to_depth(
    manipulator_id: int, depth: float, speed: int
) -> com.DriveToDepthOutputData:
    """Drive manipulator to depth

    :param manipulator_id: The ID of the manipulator to drive
    :type manipulator_id: int
    :param depth: The depth to drive to
    :type depth: float
    :param speed: The speed to drive at (in µm/s)
    :type speed: int
    :return: Callback parameters (manipulator ID, depth (or 0 on error),
    error message)
    :rtype: :class:`common.DriveToDepthOutputData`
    """
    try:
        # Check calibration status
        if not manipulators[manipulator_id].get_calibrated():
            print(f"[ERROR]\t\t Calibration not complete: {manipulator_id}\n")
            return com.DriveToDepthOutputData(0, "Manipulator not calibrated")

        # Check write state
        if not manipulators[manipulator_id].get_can_write():
            print(f"[ERROR]\t\t Cannot write to manipulator: {manipulator_id}")
            return com.DriveToDepthOutputData(0, "Cannot write to manipulator")

        return await manipulators[manipulator_id].drive_to_depth(depth, speed)

    except KeyError:
        # Manipulator not found in registered manipulators
        print(f"[ERROR]\t\t Manipulator not registered: {manipulator_id}\n")
        return com.DriveToDepthOutputData(0, "Manipulator " "not registered")


def set_inside_brain(manipulator_id: int, inside: bool) -> com.StateOutputData:
    """Set manipulator inside brain state (restricts motion)

    :param manipulator_id: The ID of the manipulator to set the state of
    :type manipulator_id: int
    :param inside: True if inside brain, False if outside
    :type inside: bool
    :return: Callback parameters (manipulator ID, inside, error message)
    :rtype: :class:`common.StateOutputData`
    """
    try:
        # Check calibration status
        if not manipulators[manipulator_id].get_calibrated():
            print("[ERROR]\t\t Calibration not complete\n")
            return com.StateOutputData(False, "Manipulator not calibrated")

        manipulators[manipulator_id].set_inside_brain(inside)
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
        print(f"[ERROR]\t\t Set manipulator {manipulator_id} inside brain " f"state")
        print(f"{e}\n")
        return com.StateOutputData(False, "Error setting " "inside brain")


async def calibrate(manipulator_id: int, sio: socketio.AsyncServer) -> str:
    """Calibrate manipulator

    :param manipulator_id: ID of manipulator to calibrate
    :type manipulator_id: int
    :param sio: SocketIO object (to call sleep)
    :type sio: :class:`socketio.AsyncServer`
    :return: Callback parameters (manipulator ID, error message)
    :rtype: str
    """
    try:
        # Check write state
        if not manipulators[manipulator_id].get_can_write():
            print(f"[ERROR]\t\t Cannot write to manipulator: {manipulator_id}")
            return "Cannot write to manipulator"

        # Move manipulator to max position
        await manipulators[manipulator_id].goto_pos([20000, 20000, 20000, 20000], 2000)

        # Call calibrate
        manipulators[manipulator_id].call_calibrate()

        # Wait for calibration to complete
        still_working = True
        while still_working:
            cur_pos = manipulators[manipulator_id].get_pos()["position"]

            # Check difference between current and target position
            for prev, cur in zip([10000, 10000, 10000, 10000], cur_pos):
                if abs(prev - cur) > 1:
                    still_working = True
                    break
                still_working = False

            # Sleep for a bit
            await sio.sleep(0.5)

        # Calibration complete
        manipulators[manipulator_id].set_calibrated()
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


def bypass_calibration(manipulator_id: int) -> str:
    """Bypass calibration of manipulator

    :param manipulator_id: ID of manipulator to bypass calibration
    :type manipulator_id: int
    :return: Callback parameters (manipulator ID, error message)
    :rtype: str
    """
    try:
        # Bypass calibration
        manipulators[manipulator_id].set_calibrated()
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


def set_can_write(
    manipulator_id: int, can_write: bool, hours: float, sio: socketio.AsyncServer
) -> com.StateOutputData:
    """Set manipulator can_write state (enables/disabled moving manipulator)

    :param manipulator_id: The ID of the manipulator to set the state of
    :type manipulator_id: int
    :param can_write: True if allowed to move, False if outside
    :type can_write: bool
    :param hours: The number of hours to allow writing (0 = forever)
    :type hours: float
    :param sio: SocketIO object from server to emit reset event
    :type sio: :class:`socketio.AsyncServer`
    :return: Callback parameters (manipulator ID, can_write, error message)
    :rtype: :class:`common.StateOutputData`
    """
    try:
        manipulators[manipulator_id].set_can_write(can_write, hours, sio)
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
