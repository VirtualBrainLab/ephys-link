import collections

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
async def connect(sid, environ, auth):
    """Acknowledge connection to the server."""
    print(f'[CONNECTION]: {sid}\n')


@sio.event
async def disconnect(sid):
    """Acknowledge disconnection from the server."""
    print(f'[DISCONNECTION]: {sid}\n')


# Events
@sio.event
async def register_manipulator(sid, manipulator_id):
    """
    Register a manipulator with the server
    :param sid: Socket session ID
    :param manipulator_id: ID of the manipulator to register
    """
    print(f'[EVENT]\t\t Register manipulator: {manipulator_id}')

    # Check if manipulator is already registered
    if manipulator_id in registered_manipulators:
        print(f'[ERROR]\t\t Manipulator already registered:'
              f' {manipulator_id}\n')
        return

    try:
        # Register manipulator
        registered_manipulators[manipulator_id] = ump.get_device(
            manipulator_id)
        print(f'[SUCCESS]\t Registered manipulator: {manipulator_id}')
    except ValueError:
        print(f'[ERROR]\t\t Manipulator not found: {manipulator_id}')
    except Exception as e:
        print(f'[ERROR]\t\t registering manipulator: {manipulator_id}')
        print(e)

    print()


@sio.event
async def get_pos(sid, manipulator_id):
    """
    Position of manipulator request
    :param sid: Socket session ID
    :param manipulator_id: ID of manipulator to pull position from
    :return: Position of manipulator in [x, y, z, w]
    """
    print(f'[MESSAGE]\t Get position of manipulator'
          f' {manipulator_id}')

    try:
        # Get position
        await sio.emit('get_pos', {
            'manipulator_id': manipulator_id,
            'pos': registered_manipulators[manipulator_id].get_pos()
        })
        print(f'[SUCCESS]\t Sent position of manipulator {manipulator_id}')
    except KeyError:
        print(f'[ERROR]\t\t Manipulator not registered: {manipulator_id}')
    except Exception as e:
        print(f'[ERROR]\t\t getting position of manipulator {manipulator_id}')
        print(e)

    print()


@sio.event
async def goto_pos(sid, data):
    """
    Move manipulator to position
    :param sid: Socket session ID
    :param data: Data containing manipulator ID, position, and speed
    :return: Position of manipulator in [x, y, z, w]
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
        return manipulator_id, True, registered_manipulators[
            manipulator_id].get_pos()
    except KeyError:
        print(f'[ERROR]\t\t Manipulator not registered: {manipulator_id}')
    except Exception as e:
        print(f'[ERROR]\t\t moving manipulator {manipulator_id} to position'
              f' {pos}')
        print(e)

    print()
    return manipulator_id, False, pos


# Start server
if __name__ == '__main__':
    # noinspection PyUnresolvedReferences
    web.run_app(app)
