import time

import socketio

sio = socketio.Client()
sio.connect("http://localhost:8081")

sio.emit("register_manipulator", "2")
sio.emit("bypass_calibration", "2")

sio.emit("set_can_write", {"manipulator_id": "2", "can_write": True, "hours": 1})

sio.emit("goto_pos", {"manipulator_id": "2", "pos": [10, 10, 10, 10], "speed": 4000})

time.sleep(1)

sio.emit("goto_pos", {"manipulator_id": "2", "pos": [0, 0, 0, 0], "speed": 4000})
