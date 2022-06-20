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
registered_manipulators_movement_queue = {}


# Handle connection events
@sio.event
async def connect(sid, environ, auth):
    """Acknowledge connection to the server."""
    print(f'[CONNECTION]: {sid}\n')


@sio.event
async def disconnect(sid):
    """Acknowledge disconnection from the server."""
    print(f'[DISCONNECTION]: {sid}\n')


# Message events
@sio.event
async def register_manipulator(sid, manipulator_id):
    """
    Register a manipulator with the server
    :param sid: Socket session ID
    :param manipulator_id: ID of the manipulator to register
    """
    print(f'[MESSAGE {sid}] Register manipulator: {manipulator_id}')

    # Check if manipulator is already registered
    if manipulator_id in registered_manipulators:
        print(f'[ERROR] Manipulator already registered: {manipulator_id}\n')
        return

    try:
        # Register manipulator
        registered_manipulators[manipulator_id] = ump.get_device(
            manipulator_id)
        print(f'[SUCCESS] Registered manipulator: {manipulator_id}')
    except ValueError:
        print(f'[ERROR] Manipulator not found: {manipulator_id}')
    except Exception as e:
        print(f'[ERROR] registering manipulator: {manipulator_id}')
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
    print(f'[MESSAGE {sid}] Get position of manipulator {manipulator_id}')

    try:
        # Get position
        await sio.emit('get_pos', {
            'manipulator_id': manipulator_id,
            'pos': registered_manipulators[manipulator_id].get_pos()
        })
        print(f'[SUCCESS] Sent position of manipulator {manipulator_id}')
    except KeyError:
        print(f'[ERROR] Manipulator not registered: {manipulator_id}')
    except Exception as e:
        print(f'[ERROR] getting position of manipulator {manipulator_id}')
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
        f'[MESSAGE {sid}] Move manipulator {manipulator_id} to position {pos}'
    )

    try:
        # Wait for last movement to finish
        registered_manipulators_movement_queue[manipulator_id][
            0].finished_event.wait()
    except KeyError:
        # A queue for this manipulator doesn't exist yet
        pass
    except IndexError:
        # The queue for this manipulator is empty
        pass
    except Exception as e:
        print(f'[ERROR] waiting for last movement to finish: {manipulator_id}')
        print(e)
        return

    try:
        # Move manipulator
        movement = registered_manipulators[manipulator_id].goto_pos(pos, speed)

        try:
            # Add movement to queue
            registered_manipulators_movement_queue[manipulator_id].appendleft(
                movement)
        except KeyError:
            # Create movement queue
            registered_manipulators_movement_queue[manipulator_id] = \
                collections.deque([movement])
        except Exception as e:
            print(f'[ERROR] adding movement to queue: {manipulator_id}')
            print(e)
            return

        # Wait for movement to finish
        movement.finished_event.wait()

        print(
            f'[SUCCESS] Moved manipulator {manipulator_id} to position {pos}\n'
        )
        await sio.emit('goto_pos',
                       {'manipulator_id': manipulator_id, 'pos': pos})
    except KeyError:
        print(f'[ERROR] Manipulator not registered: {manipulator_id}')
    except Exception as e:
        print(f'[ERROR] moving manipulator {manipulator_id} to position {pos}')
        print(e)

    print()


# Start server
if __name__ == '__main__':
    # noinspection PyUnresolvedReferences
    web.run_app(app)
