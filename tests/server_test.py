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


# Message events
@sio.event
def message(data):
    """Receive message from the server."""
    print('message received: ', data)


# Connect to the server and send message
sio.connect('http://localhost:5000')
sio.emit('message', 'hello world')
sio.wait()
