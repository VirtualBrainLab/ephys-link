import eventlet
import socketio

# Setup server
sio = socketio.Server()
app = socketio.WSGIApp(sio)


# Handle connection events
@sio.event
def connect(sid, environ, auth):
    print('Connection: ', sid)


@sio.event
def disconnect(sid):
    print('Disconnect: ', sid)


# Message
@sio.event
def message(sid, data):
    print(sid, ' says: ', data)
    sio.emit('message', [1, 2, 3, 4])


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
