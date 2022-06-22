from typing import List

from manipulator import Manipulator
from pathlib import Path
from sensapex import UMP, UMError

# Setup Sensapex
UMP.set_library_path(str(Path(__file__).parent.absolute()) + '/resources/')
ump = UMP.get_ump()

# Registered manipulators
manipulators = {}


def reset():
    """Reset handler"""
    manipulators.clear()


def register_manipulator(manipulator_id: int) -> (int, str):
    """
    Register a manipulator
    :param manipulator_id: The ID of the manipulator to register.
    :return: Callback parameters [manipulator_id, error message (on error)]
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


def get_pos(manipulator_id: int) -> (int, List[float], str):
    """
    Get the current position of a manipulator
    :param manipulator_id: The ID of the manipulator to get the position of.
    :return: Callback parameters [Manipulator ID, position in [x, y, z,
    w] (or an empty array on error), error message]
    """
    try:
        # Check calibration status
        if not manipulators[manipulator_id].get_calibrated():
            print(f'[ERROR]\t\t Calibration not complete\n')
            return manipulator_id, [], 'Manipulator not calibrated'

        # Get position
        return manipulators[manipulator_id].get_pos()

    except KeyError:
        # Manipulator not found in registered manipulators
        print(f'[ERROR]\t\t Manipulator not registered: {manipulator_id}')
        return manipulator_id, [], 'Manipulator not registered'


def goto_pos(manipulator_id: int, position: List[float], speed: int) -> (
        int, List[float], str):
    """
    Move manipulator to position
    :param manipulator_id: The ID of the manipulator to move
    :param position: The position to move to
    :param speed: The speed to move at (in um/s)
    :return: Callback parameters [Manipulator ID, position in [x, y, z,
    w] (or an empty array on error), error message]
    """
    try:
        # Check calibration status
        if not manipulators[manipulator_id].get_calibrated():
            print(f'[ERROR]\t\t Calibration not complete\n')
            return manipulator_id, [], 'Manipulator not calibrated'

        # Move manipulator
        movement = manipulators[manipulator_id].get_device().goto_pos(position,
                                                                      speed)

        # Wait for movement to finish
        movement.finished_event.wait()

        # Get position
        manipulator_final_position = manipulators[
            manipulator_id].device.get_pos()

        print(
            f'[SUCCESS]\t Moved manipulator {manipulator_id} to position'
            f' {manipulator_final_position}\n'
        )
        return manipulator_id, manipulator_final_position, ''

    except KeyError:
        # Manipulator not found in registered manipulators
        print(f'[ERROR]\t\t Manipulator not registered: {manipulator_id}\n')
        return manipulator_id, [], 'Manipulator not registered'

    except Exception as e:
        # Other error
        print(f'[ERROR]\t\t Moving manipulator {manipulator_id} to position'
              f' {position}')
        print(f'{e}\n')
        return manipulator_id, [], 'Error moving manipulator'


async def calibrate(manipulator_id: int, sio) -> (int, str):
    """
        Calibrate manipulator
        :param manipulator_id: ID of manipulator to calibrate
        :param sio: SocketIO object (to call sleep)
        :return: Callback parameters [Manipulator ID, error message]
        """
    try:
        # Move manipulator to max position
        move = manipulators[manipulator_id].device.goto_pos(
            [20000, 20000,
             20000, 20000],
            2000)
        move.finished_event.wait()

        # Call calibrate
        manipulators[manipulator_id].device.calibrate_zero_position()
        await sio.sleep(70)
        manipulators[manipulator_id].set_calibrated()
        return manipulator_id, ''

    except KeyError:
        # Manipulator not found in registered manipulators
        print(f'[ERROR]\t\t Manipulator not registered: {manipulator_id}\n')
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
    :return: Callback parameters [Manipulator ID, error message]
    """
    try:
        # Bypass calibration
        manipulators[manipulator_id].set_calibrated()
        return manipulator_id, ''

    except KeyError:
        # Manipulator not found in registered manipulators
        print(f'[ERROR]\t\t Manipulator not registered: {manipulator_id}\n')
        return manipulator_id, 'Manipulator not registered'

    except Exception as e:
        # Other error
        print(
            f'[ERROR]\t\t Bypass calibration of manipulator {manipulator_id}')
        print(f'{e}\n')
        return manipulator_id, 'Error bypassing calibration'
