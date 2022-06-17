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
def message(sid, data):
    """Receive message from the a client and respond."""
    print(f'[MESSAGE {sid}]: {data}')
    sio.emit('message', [1, 2, 3, 4])


@sio.event
def register_manipulator(sid, manipulator_id):
    """
    Register a manipulator with the server
    :param sid: Socket session ID
    :param manipulator_id: ID of the manipulator to register
    :return:
    """
    print(f'[MESSAGE {sid}] Register manipulator: {manipulator_id}')
    if manipulator_id not in registered_manipulators:
        registered_manipulators[manipulator_id] = ump.get_device(
            manipulator_id)
        print(f'Registered manipulator: {manipulator_id}')
    else:
        print(f'Manipulator already registered: {manipulator_id}')


# @sio.event
# def pos(sid, manipulator_id):
#     """
#     Position of manipulator request
#     :param sid: Socket session ID
#     :param manipulator_id: ID of manipulator to pull position from
#     :return: Position of manipulator in [x, y, z, w]
#     """


# Start server
if __name__ == '__main__':
    # noinspection PyUnresolvedReferences
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
