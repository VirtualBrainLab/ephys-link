from manipulator import Manipulator
from pathlib import Path
from sensapex import UMP, UMError

# Setup Sensapex
UMP.set_library_path(str(Path(__file__).parent.absolute()) + '/resources/')
ump = UMP.get_ump()

# Registered manipulators
manipulators = {}


def register_manipulator(manipulator_id: int):
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


def get_pos(manipulator_id: int):
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
        position = manipulators[manipulator_id].device.get_pos()
        print(f'[SUCCESS]\t Sent position of manipulator {manipulator_id}\n')
        return manipulator_id, position, ''

    except KeyError:
        # Manipulator not found in registered manipulators
        print(f'[ERROR]\t\t Manipulator not registered: {manipulator_id}')
        return manipulator_id, [], 'Manipulator not registered'

    except Exception as e:
        # Other error
        print(f'[ERROR]\t\t Getting position of manipulator {manipulator_id}')
        print(f'{e}\n')
        return manipulator_id, [], 'Error getting position'
