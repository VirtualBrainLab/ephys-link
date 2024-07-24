from asyncio import run

from vbl_aquarium.models.ephys_link import EphysLinkOptions, SetPositionRequest
from vbl_aquarium.models.unity import Vector4

from ephys_link.back_end.platform_handler import PlatformHandler
from ephys_link.util.console import Console

c = Console(enable_debug=True)
p = PlatformHandler(EphysLinkOptions(type="pathfinder-mpm"), c)
target = Vector4()
# target = Vector4(x=10, y=10, z=10, w=10)

print(run(p.set_position(SetPositionRequest(manipulator_id="A", position=target, speed=5))).to_json_string())
print("Done!")
