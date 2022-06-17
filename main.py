import eventlet
# noinspection PyPackageRequirements
import socketio
from sensapex import UMP

# Setup server
sio = socketio.Server()
app = socketio.WSGIApp(sio)

# Setup Sensapex
ump = UMP.get_ump()
registered_manipulators = {}


# Handle connection events
@sio.event
def connect(sid, environ, auth):
    """Acknowledge connection to the server."""
    print(f'[CONNECTION]: {sid}')


@sio.event
def disconnect(sid):
    """Acknowledge disconnection from the server."""
    print(f'[DISCONNECTION]: {sid}')


# Message events
@sio.event
def register_manipulator(sid, manipulator_id):
    """
    Register a manipulator with the server
    :param sid: Socket session ID
    :param manipulator_id: ID of the manipulator to register
    """
    print(f'[MESSAGE {sid}] Register manipulator: {manipulator_id}')

    # Check if manipulator is already registered
    if manipulator_id in registered_manipulators:
        print(f'Manipulator already registered: {manipulator_id}')
        return

    # Register manipulator
    registered_manipulators[manipulator_id] = ump.get_device(manipulator_id)
    print(f'Registered manipulator: {manipulator_id}')


@sio.event
def get_pos(sid, manipulator_id):
    """
    Position of manipulator request
    :param sid: Socket session ID
    :param manipulator_id: ID of manipulator to pull position from
    :return: Position of manipulator in [x, y, z, w]
    """
    print(f'[MESSAGE {sid}] Get position of manipulator {manipulator_id}')

    # Check if manipulator is registered
    if manipulator_id not in registered_manipulators:
        print(f'Manipulator not registered: {manipulator_id}')
        return

    # Get position
    sio.emit('get_pos', {
        'manipulator_id': manipulator_id,
        'pos': registered_manipulators[manipulator_id].get_pos()
    })


# Start server
if __name__ == '__main__':
    # noinspection PyUnresolvedReferences
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
