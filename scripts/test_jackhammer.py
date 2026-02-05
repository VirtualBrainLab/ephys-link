from socketio import SimpleClient

sio = SimpleClient()
sio.connect("http://localhost:3000")
result = sio.call("jackhammer", '''{
    "manipulator_id": "6",
    "iterations": 3,
    "phase1_steps": 1,
    "phase1_pulses": 80,
    "phase2_steps": 1,
    "phase2_pulses": -80
}''')
print(result)
sio.disconnect()