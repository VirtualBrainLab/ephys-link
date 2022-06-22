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
