from socketio import SimpleClient

sio = SimpleClient()
sio.connect("http://localhost:3000")
result = sio.call("jackhammer", '''{
    "manipulator_id": "6",
    "iterations": 20,
    "phase1_steps": 10,
    "phase1_pulses": 15,
    "phase2_steps": 5,
    "phase2_pulses": -15
}''')
print(result)
sio.disconnect()