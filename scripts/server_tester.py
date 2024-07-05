from socketio import SimpleClient
from vbl_aquarium.models.ephys_link import GotoPositionRequest, InsideBrainRequest, DriveToDepthRequest
from vbl_aquarium.models.unity import Vector4
from time import sleep

with SimpleClient() as sio:
    sio.connect("http://localhost:3000")
    
    print(sio.call("set_inside_brain", InsideBrainRequest(manipulator_id="6", inside=True).to_string()))

    target = Vector4()
    # target = Vector4(x=10, y=10, z=10, w=10)

    sio.emit(
        "set_depth",
        DriveToDepthRequest(manipulator_id="6", depth=10, speed=3).to_string(),
    )
    sleep(1)
    print(sio.call("stop"))
    # while True:
    #     print(sio.call("get_position", "6"))
    sio.disconnect()
