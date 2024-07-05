from time import sleep

from socketio import SimpleClient
from vbl_aquarium.models.ephys_link import SetDepthRequest, SetInsideBrainRequest
from vbl_aquarium.models.unity import Vector4

with SimpleClient() as sio:
    sio.connect("http://localhost:3000")

    print(sio.call("set_inside_brain", SetInsideBrainRequest(manipulator_id="6", inside=True).to_json_string()))

    target = Vector4()
    # target = Vector4(x=10, y=10, z=10, w=10)

    sio.emit(
        "set_depth",
        SetDepthRequest(manipulator_id="6", depth=10, speed=3).to_json_string(),
    )
    sleep(1)
    print(sio.call("stop"))
    # while True:
    #     print(sio.call("get_position", "6"))
    sio.disconnect()
