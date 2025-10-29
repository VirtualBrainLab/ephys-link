from asyncio import run

from vbl_aquarium.models.ephys_link import SetDepthRequest
from vbl_aquarium.models.unity import Vector4

from ephys_link.back_end.platform_handler import PlatformHandler
from ephys_link.bindings.mpm_binding import MPMBinding
from ephys_link.front_end.console import Console

c = Console(enable_debug=True)
p = PlatformHandler(MPMBinding(), c)
# target = Vector4()
target = Vector4(x=7.5, y=7.5, z=7.5, w=7.5)

# print(run(p.set_position(SetPositionRequest(manipulator_id="A", position=target, speed=5))).to_json_string())
print(run(p.set_depth(SetDepthRequest(manipulator_id="A", depth=7.5, speed=0.15))).to_json_string())
print("Done!")
