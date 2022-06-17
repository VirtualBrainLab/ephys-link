import eventlet
# noinspection PyPackageRequirements
import socketio

# Setup server
sio = socketio.Server()
app = socketio.WSGIApp(sio)


# Handle connection events
@sio.event
def connect(sid, environ, auth):
    """Acknowledge connection to the server."""
    print('Connection: ', sid)


@sio.event
def disconnect(sid):
    """Acknowledge disconnection from the server."""
    print('Disconnect: ', sid)


# Message
@sio.event
def message(sid, data):
    """Receive message from the a client and respond."""
    print(sid, ' says: ', data)
    sio.emit('message', [1, 2, 3, 4])


# Start server
if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
