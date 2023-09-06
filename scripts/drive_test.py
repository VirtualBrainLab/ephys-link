import time

import socketio

sio = socketio.Client()
sio.connect("http://localhost:8081")

manipulator_id = "0"

sio.emit("register_manipulator", manipulator_id)
sio.emit("bypass_calibration", manipulator_id)

sio.emit(
    "set_can_write", {"manipulator_id": manipulator_id, "can_write": True, "hours": 1}
)

sio.emit(
    "goto_pos",
    {"manipulator_id": manipulator_id, "pos": [10, 10, 10, 10], "speed": 4},
)

time.sleep(1)

sio.emit(
    "goto_pos", {"manipulator_id": manipulator_id, "pos": [0, 0, 0, 0], "speed": 4}
)
