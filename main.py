from aiohttp import web
# noinspection PyPackageRequirements
import socketio
from sensapex import UMP

# Setup server
sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

# Setup Sensapex
ump = UMP.get_ump()
registered_manipulators = {}


# Handle connection events
@sio.event
async def connect(sid, _, __):
    """
    Acknowledge connection to the server
    :param sid: Socket session ID
    :param _: WSGI formatted dictionary with request info (unused)
    :param __: Authentication details (unused)
    """
    print(f'[CONNECTION]:\t\t {sid}\n')


@sio.event
async def disconnect(sid):
    """
    Acknowledge disconnection from the server
    :param sid: Socket session ID
    """
    print(f'[DISCONNECTION]:\t {sid}\n')
    registered_manipulators.clear()


# Events
@sio.event
async def register_manipulator(_, manipulator_id):
    """
    Register a manipulator with the server
    :param _: Socket session ID (unused)
    :param manipulator_id: ID of the manipulator to register
    :return: Error message if error, otherwise an empty string
    """
    print(f'[EVENT]\t\t Register manipulator: {manipulator_id}')

    # Check if manipulator is already registered
    if manipulator_id in registered_manipulators:
        print(f'[ERROR]\t\t Manipulator already registered:'
              f' {manipulator_id}\n')
        return manipulator_id, 'Manipulator already registered'

    try:
        # Register manipulator
        registered_manipulators[manipulator_id] = ump.get_device(
            manipulator_id)
        print(f'[SUCCESS]\t Registered manipulator: {manipulator_id}\n')
        return manipulator_id, ''

    except ValueError:
        # Manipulator not found in UMP
        print(f'[ERROR]\t\t Manipulator not found: {manipulator_id}\n')
        return manipulator_id, 'Manipulator not found'

    except Exception as e:
        # Other error
        print(f'[ERROR]\t\t registering manipulator: {manipulator_id}')
        print(f'{e}\n')
        return manipulator_id, 'Error registering manipulator'


@sio.event
async def get_pos(_, manipulator_id):
    """
    Position of manipulator request
    :param _: Socket session ID (unused)
    :param manipulator_id: ID of manipulator to pull position from
    :return: [Manipulator ID, position in [x, y, z, w] (or an empty array
    on error), error message]
    """
    print(f'[EVENT]\t\t Get position of manipulator'
          f' {manipulator_id}')

    try:
        # Get position
        position = registered_manipulators[manipulator_id].get_pos()
        print(f'[SUCCESS]\t Sent position of manipulator {manipulator_id}\n')
        return manipulator_id, position, ''

    except KeyError:
        # Manipulator not found in registered manipulators
        print(f'[ERROR]\t\t Manipulator not registered: {manipulator_id}\n')
        return manipulator_id, [], 'Manipulator not registered'

    except Exception as e:
        # Other error
        print(f'[ERROR]\t\t getting position of manipulator {manipulator_id}')
        print(f'{e}\n')
        return manipulator_id, [], 'Error getting position'


@sio.event
async def goto_pos(_, data):
    """
    Move manipulator to position
    :param _: Socket session ID (unused)
    :param data: Data containing manipulator ID, position, and speed
    :return: [Manipulator ID, position in [x, y, z, w] (or an empty array on
    error), error message]
    """
    manipulator_id = data['manipulator_id']
    pos = data['pos']
    speed = data['speed']
    print(
        f'[EVENT]\t\t Move manipulator {manipulator_id} '
        f'to position {pos}'
    )

    try:
        # Move manipulator
        movement = registered_manipulators[manipulator_id].goto_pos(pos, speed)

        # Wait for movement to finish
        movement.finished_event.wait()

        print(
            f'[SUCCESS]\t Moved manipulator {manipulator_id} to position'
            f' {pos}\n'
        )
        return manipulator_id, registered_manipulators[
            manipulator_id].get_pos(), ''

    except KeyError:
        # Manipulator not found in registered manipulators
        print(f'[ERROR]\t\t Manipulator not registered: {manipulator_id}\n')
        return manipulator_id, [], 'Manipulator not registered'

    except Exception as e:
        # Other error
        print(f'[ERROR]\t\t moving manipulator {manipulator_id} to position'
              f' {pos}')
        print(f'{e}\n')
        return manipulator_id, [], 'Error moving manipulator'


@sio.on('*')
async def catch_all(_, data):
    """
    Catch all event
    :param _: Socket session ID (unused)
    :param data: Data received from client
    """
    print(f'[UNKNOWN EVENT]:\t {data}')


# Start server
if __name__ == '__main__':
    web.run_app(app)
