from socketio import SimpleClient
from vbl_aquarium.models.ephys_link import GotoPositionRequest
from vbl_aquarium.models.unity import Vector4

with SimpleClient() as sio:
    sio.connect("http://localhost:3000")

    target = Vector4()
    # target = Vector4(x=10, y=10, z=10, w=10)

    sio.emit(
        "set_position",
        GotoPositionRequest(manipulator_id="6", position=target, speed=5).to_string(),
    )
    while True:
        print(sio.call("get_position", "6"))
