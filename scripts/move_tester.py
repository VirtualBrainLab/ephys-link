import json

import socketio

if __name__ == "__main__":
    sio = socketio.Client()
    sio.connect("http://localhost:8081")

    sio.emit("register_manipulator", "6")
    sio.emit("bypass_calibration", "6")
    sio.emit("set_can_write", json.dumps({"manipulator_id": "6", "can_write": True, "hours": 0}))

    end = ""
    while end == "":
        sio.emit("goto_pos", json.dumps({"manipulator_id": "6", "pos": [0, 10, 10, 10], "speed": 0.5}))

        input("Press enter to continue...")

        sio.emit("goto_pos", json.dumps({"manipulator_id": "6", "pos": [10, 10, 10, 10], "speed": 1}))

        end = input("Press enter to continue (or type any key then enter to end)...")
