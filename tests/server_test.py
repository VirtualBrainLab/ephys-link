import socketio

sio = socketio.Client()


# Connection events
@sio.event
def connect():
    print('connection established')


@sio.event
def disconnect():
    print('disconnected from server')


# Message events
@sio.event
def message(data):
    print('message received: ', data)


sio.connect('http://localhost:5000')
sio.emit('message', 'hello world')
sio.wait()
