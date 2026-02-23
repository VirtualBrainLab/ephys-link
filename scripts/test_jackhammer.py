from socketio import SimpleClient


#  .\venv\Scripts\Activate.ps1
#  ephys-link -b -t ump
#  python scripts/test_jackhammer.py
sio = SimpleClient()
sio.connect("http://localhost:3000")
result = sio.call("jackhammer", '''{
    "manipulator_id": "4",
    "iterations": 2,
    "phase1_steps": 1,
    "phase1_pulses": 80,
    "phase2_steps": 1,
    "phase2_pulses": -80
}''')
print(result)
sio.disconnect()