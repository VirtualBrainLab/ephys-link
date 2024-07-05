from asyncio import run

from vbl_aquarium.models.ephys_link import SetPositionRequest
from vbl_aquarium.models.unity import Vector4

from ephys_link.back_end.platform_handler import PlatformHandler
from ephys_link.util.console import Console

c = Console(enable_debug=True)
p = PlatformHandler("ump-4", c)
target = Vector4()
# target = Vector4(x=10, y=10, z=10, w=10)

print(run(p.set_position(SetPositionRequest(manipulator_id="6", position=target, speed=5))).to_json_string())
print("Done!")
