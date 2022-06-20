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


# Event callbacks
def goto_callback(manipulator_id, success, position):
    """
    Callback for the goto command
    :param manipulator_id: Response from the server
    :param success: Success of the command
    :param position: Position of the manipulator
    """
    print(
        f'[MESSAGE]: Manipulator {manipulator_id} '
        f'{"successfully" if success else "unsuccessfully"}'
        f' moved to position: {position}'
    )


# Connect to the server and send message
sio.connect('http://localhost:8080')
sio.emit('register_manipulator', 1)
sio.emit('register_manipulator', 2)
for _ in range(2):
    sio.emit('goto_pos', {'manipulator_id': 1, 'pos': [0, 0, 0, 0],
                          'speed': 2000}, callback=goto_callback)
    sio.emit('goto_pos', {'manipulator_id': 2, 'pos': [0, 0, 0, 0],
                          'speed': 2000}, callback=goto_callback)

    sio.emit('goto_pos', {'manipulator_id': 1, 'pos': [10000, 10000, 10000,
                                                       10000],
                          'speed': 2000}, callback=goto_callback)
    sio.emit('goto_pos', {'manipulator_id': 2, 'pos': [10000, 10000, 10000,
                                                       10000],
                          'speed': 2000}, callback=goto_callback)
sio.wait()
