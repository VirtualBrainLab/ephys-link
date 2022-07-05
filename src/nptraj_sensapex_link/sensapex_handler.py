import time
from pathlib import Path
from typing import TypedDict
from sensapex import UMP, UMError
from serial import Serial
from serial.tools.list_ports import comports
from manipulator import Manipulator

# Registered manipulators
manipulators = {}

# Setup Sensapex
UMP.set_library_path(str(Path(__file__).parent.absolute()) + '/resources/')
ump = UMP.get_ump()

# Setup Arduino serial port
target_port = None
poll_rate = 0.05
continue_polling = True

# Search for serial ports
for port, desc, _ in comports():
    if 'USB Serial Device' in desc:
        target_port = port
        break


def poll_serial():
    """Continuously poll serial port for data"""
    ser = Serial(target_port, 9600, timeout=poll_rate)
    while continue_polling:
        if ser.in_waiting > 0:
            ser.readline()
            # Cause a break
            print('STOPPING EVERYTHING')
            stop()
            ser.reset_input_buffer()
        time.sleep(poll_rate)
    ser.close()


# Data formats
class GotoPositionDataFormat(TypedDict):
    """Data format for goto_pos"""
    manipulator_id: int
    pos: list[float]
    speed: int


class InsideBrainDataFormat(TypedDict):
    """Data format for inside_brain"""
    manipulator_id: int
    inside: bool


class DriveToDepthDataFormat(TypedDict):
    """Data format for drive_to_depth"""
    manipulator_id: int
    depth: float
    speed: int


class CanWriteDataFormat(TypedDict):
    """Data format for can_write"""
    manipulator_id: int
    can_write: bool
    hours: float


# Event handlers
def reset() -> bool:
    """
    Reset handler
    :return: True if successful, False otherwise
    """
    stop_result = stop()
    manipulators.clear()
    return stop_result


def stop() -> bool:
    """
    Stop handler
    :return: True if successful, False otherwise
    """
    try:
        for manipulator in manipulators.values():
            manipulator.stop()
        return True
    except Exception as e:
        print(f'[ERROR]\t\t Stopping manipulators: {e}\n')
        return False


def register_manipulator(manipulator_id: int) -> (int, str):
    """
    Register a manipulator
    :param manipulator_id: The ID of the manipulator to register.
    :return: Callback parameters (manipulator_id, error message (on error))
    """
    # Check if manipulator is already registered
    if manipulator_id in manipulators:
        print(f'[ERROR]\t\t Manipulator already registered:'
              f' {manipulator_id}\n')
        return manipulator_id, 'Manipulator already registered'

    try:
        # Register manipulator
        manipulators[manipulator_id] = Manipulator(
            ump.get_device(manipulator_id))

        print(f'[SUCCESS]\t Registered manipulator: {manipulator_id}\n')
        return manipulator_id, ''

    except ValueError:
        # Manipulator not found in UMP
        print(f'[ERROR]\t\t Manipulator not found: {manipulator_id}\n')
        return manipulator_id, 'Manipulator not found'

    except Exception as e:
        # Other error
        print(f'[ERROR]\t\t Registering manipulator: {manipulator_id}')
        print(f'{e}\n')
        return manipulator_id, 'Error registering manipulator'


def get_pos(manipulator_id: int) -> (int, tuple[float], str):
    """
    Get the current position of a manipulator
    :param manipulator_id: The ID of the manipulator to get the position of.
    :return: Callback parameters (manipulator ID, position in (x, y, z,
    w) (or an empty array on error), error message)
    """
    try:
        # Check calibration status
        if not manipulators[manipulator_id].get_calibrated():
            print(f'[ERROR]\t\t Calibration not complete: {manipulator_id}\n')
            return manipulator_id, (), 'Manipulator not calibrated'

        # Get position
        return manipulators[manipulator_id].get_pos()

    except KeyError:
        # Manipulator not found in registered manipulators
        print(f'[ERROR]\t\t Manipulator not registered: {manipulator_id}')
        return manipulator_id, (), 'Manipulator not registered'


async def goto_pos(manipulator_id: int, position: list[float], speed: int) \
        -> (int, tuple[float], str):
    """
    Move manipulator to position
    :param manipulator_id: The ID of the manipulator to move
    :param position: The position to move to
    :param speed: The speed to move at (in µm/s)
    :return: Callback parameters (manipulator ID, position in (x, y, z,
    w) (or an empty array on error), error message)
    """
    try:
        # Check calibration status
        if not manipulators[manipulator_id].get_calibrated():
            print(f'[ERROR]\t\t Calibration not complete: {manipulator_id}\n')
            return manipulator_id, (), 'Manipulator not calibrated'

        # Check write state
        if not manipulators[manipulator_id].get_can_write():
            print(f'[ERROR]\t\t Cannot write to manipulator: {manipulator_id}')
            return manipulator_id, (), 'Cannot write to manipulator'

        return await manipulators[manipulator_id].goto_pos(position, speed)

    except KeyError:
        # Manipulator not found in registered manipulators
        print(f'[ERROR]\t\t Manipulator not registered: {manipulator_id}\n')
        return manipulator_id, (), 'Manipulator not registered'


async def drive_to_depth(manipulator_id: int, depth: float, speed: int) \
        -> (int, float, str):
    """
    Drive manipulator to depth
    :param manipulator_id: The ID of the manipulator to drive
    :param depth: The depth to drive to
    :param speed: The speed to drive at (in µm/s)
    :return: Callback parameters (manipulator ID, depth (or 0 on error),
    error message)
    """
    try:
        # Check calibration status
        if not manipulators[manipulator_id].get_calibrated():
            print(f'[ERROR]\t\t Calibration not complete: {manipulator_id}\n')
            return manipulator_id, 0, 'Manipulator not calibrated'

        # Check write state
        if not manipulators[manipulator_id].get_can_write():
            print(f'[ERROR]\t\t Cannot write to manipulator: {manipulator_id}')
            return manipulator_id, 0, 'Cannot write to manipulator'

        return await manipulators[manipulator_id].drive_to_depth(depth, speed)

    except KeyError:
        # Manipulator not found in registered manipulators
        print(f'[ERROR]\t\t Manipulator not registered: {manipulator_id}\n')
        return manipulator_id, 0, 'Manipulator not registered'


async def set_inside_brain(manipulator_id: int, inside: bool) -> \
        (int, bool, str):
    """
    Set manipulator inside brain state (restricts motion)
    :param manipulator_id: The ID of the manipulator to set the state of
    :param inside: True if inside brain, False if outside
    :return: Callback parameters (manipulator ID, inside, error message)
    """
    try:
        # Check calibration status
        if not manipulators[manipulator_id].get_calibrated():
            print(f'[ERROR]\t\t Calibration not complete\n')
            return manipulator_id, 'Manipulator not calibrated'

        manipulators[manipulator_id].set_inside_brain(inside)
        print(f'[SUCCESS]\t Set inside brain state for manipulator:'
              f' {manipulator_id}\n')
        return manipulator_id, inside, ''

    except KeyError:
        # Manipulator not found in registered manipulators
        print(f'[ERROR]\t\t Manipulator {manipulator_id} not registered\n')
        return manipulator_id, False, 'Manipulator not registered'

    except Exception as e:
        # Other error
        print(f'[ERROR]\t\t Set manipulator {manipulator_id} inside brain '
              f'state')
        print(f'{e}\n')
        return manipulator_id, False, 'Error setting inside brain'


async def calibrate(manipulator_id: int, sio) -> (int, str):
    """
        Calibrate manipulator
        :param manipulator_id: ID of manipulator to calibrate
        :param sio: SocketIO object (to call sleep)
        :return: Callback parameters (manipulator ID, error message)
        """
    try:
        # Check write state
        if not manipulators[manipulator_id].get_can_write():
            print(f'[ERROR]\t\t Cannot write to manipulator: {manipulator_id}')
            return manipulator_id, 'Cannot write to manipulator'

        # Move manipulator to max position
        await manipulators[manipulator_id].goto_pos([20000, 20000, 20000,
                                                     20000], 2000)

        # Call calibrate
        manipulators[manipulator_id].call_calibrate()
        await sio.sleep(70)
        manipulators[manipulator_id].set_calibrated()
        print(f'[SUCCESS]\t Calibrated manipulator {manipulator_id}\n')
        return manipulator_id, ''

    except KeyError:
        # Manipulator not found in registered manipulators
        print(f'[ERROR]\t\t Manipulator {manipulator_id} not registered\n')
        return manipulator_id, 'Manipulator not registered'

    except UMError as e:
        # SDK call error
        print(f'[ERROR]\t\t Calling calibrate manipulator {manipulator_id}')
        print(f'{e}\n')
        return manipulator_id, 'Error calling calibrate'

    except Exception as e:
        # Other error
        print(f'[ERROR]\t\t Calibrate manipulator {manipulator_id}')
        print(f'{e}\n')
        return manipulator_id, 'Error calibrating manipulator'


def bypass_calibration(manipulator_id: int) -> (int, str):
    """
    Bypass calibration of manipulator
    :param manipulator_id: ID of manipulator to bypass calibration
    :return: Callback parameters (manipulator ID, error message)
    """
    try:
        # Bypass calibration
        manipulators[manipulator_id].set_calibrated()
        print(
            f'[SUCCESS]\t Bypassed calibration for manipulator'
            f' {manipulator_id}\n')
        return manipulator_id, ''

    except KeyError:
        # Manipulator not found in registered manipulators
        print(f'[ERROR]\t\t Manipulator {manipulator_id} not registered\n')
        return manipulator_id, 'Manipulator not registered'

    except Exception as e:
        # Other error
        print(
            f'[ERROR]\t\t Bypass calibration of manipulator {manipulator_id}')
        print(f'{e}\n')
        return manipulator_id, 'Error bypassing calibration'


def set_can_write(manipulator_id: int, can_write: bool, hours: float,
                  sio) -> (int, bool, str):
    """
    Set manipulator can_write state (enables/disabled moving manipulator)
    :param sio:
    :param manipulator_id: The ID of the manipulator to set the state of
    :param can_write: True if allowed to move, False if outside
    :param hours: The number of hours to allow writing (0 = forever)
    :param sio: SocketIO object from server to emit reset event
    :return: Callback parameters (manipulator ID, can_write, error message)
    """
    try:
        manipulators[manipulator_id].set_can_write(can_write, hours, sio)
        print(f'[SUCCESS]\t Set can_write state for manipulator'
              f' {manipulator_id}\n')
        return manipulator_id, can_write, ''

    except KeyError:
        # Manipulator not found in registered manipulators
        print(f'[ERROR]\t\t Manipulator not registered: {manipulator_id}\n')
        return manipulator_id, False, 'Manipulator not registered'

    except Exception as e:
        # Other error
        print(f'[ERROR]\t\t Set manipulator {manipulator_id} can_write state')
        print(f'{e}\n')
        return manipulator_id, False, 'Error setting can_write'
