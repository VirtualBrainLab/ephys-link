# noinspection PyPackageRequirements
import socketio

sio = socketio.Client()


# Connection events
@sio.event
def connect():
    """Acknowledge connection to the server."""
    print('connection established')


@sio.event
def disconnect():
    """Acknowledge disconnection from the server."""
    print('disconnected from server')


# Message handlers
@sio.event
def get_pos(data):
    """
    Received position message from the server
    :param data: Position data
    """
    manipulator_id = data['manipulator_id']
    pos = data['pos']
    print(
        f'[MESSAGE]: Received position for manipulator {manipulator_id}: {pos}'
    )


# Connect to the server and send message
sio.connect('http://localhost:8080')
sio.emit('get_pos', 1)
sio.emit('register_manipulator', 1)
sio.emit('register_manipulator', 2)
sio.emit('get_pos', 1)
sio.emit('get_pos', 2)
sio.wait()
