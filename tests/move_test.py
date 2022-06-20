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
def goto_pos(data):
    """
    Received position message from the server
    :param data: Position data
    """
    manipulator_id = data['manipulator_id']
    pos = data['pos']
    print(f'[MESSAGE]: Manipulator {manipulator_id} moved to position: {pos}')


# Connect to the server and send message
sio.connect('http://localhost:8080')
sio.emit('register_manipulator', 1)
sio.emit('register_manipulator', 2)
sio.emit('goto_pos', {'manipulator_id': 1, 'pos': [0, 0, 0, 0],
                      'speed': 1000})
sio.emit('goto_pos', {'manipulator_id': 2, 'pos': [0, 0, 0, 0],
                      'speed': 1000})
#
sio.emit('goto_pos', {'manipulator_id': 1, 'pos': [10000, 10000, 10000, 10000],
                      'speed': 1000})
sio.emit('goto_pos', {'manipulator_id': 2, 'pos': [10000, 10000, 10000, 10000],
                      'speed': 1000})
sio.wait()
