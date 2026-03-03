from socketio import SimpleClient

sio = SimpleClient()
sio.connect("http://localhost:3000")

# Closed-loop test: advance 50 µm (longer timeout)
result = sio.call("jackhammer", '''{
    "manipulator_id": "6",
    "closed_loop": true,
    "target_um": 50,
    "phase1_steps": 2,
    "phase1_pulses": 70,
    "phase2_steps": 2,
    "phase2_pulses": -70
}''', timeout=120)

print(result)
sio.disconnect()