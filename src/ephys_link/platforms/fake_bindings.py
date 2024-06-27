from vbl_aquarium.models.unity import Vector3, Vector4

from ephys_link.util.base_bindings import BaseBindings


class FakeBindings(BaseBindings):
    def __init__(self) -> None:
        """Initialize fake manipulator infos."""

        self._positions = [Vector4() for _ in range(8)]
        self._angles = [
            Vector3(x=90, y=60, z=0),
            Vector3(x=-90, y=60, z=0),
            Vector3(x=180, y=60, z=0),
            Vector3(x=0, y=60, z=0),
            Vector3(x=45, y=30, z=0),
            Vector3(x=-45, y=30, z=0),
            Vector3(x=135, y=30, z=0),
            Vector3(x=-135, y=30, z=0),
        ]

    async def get_manipulators(self) -> list[str]:
        return list(map(str, range(8)))

    async def get_num_axes(self) -> int:
        return 4

    async def get_dimensions(self) -> Vector4:
        return Vector4(x=20, y=20, z=20, w=20)

    async def get_position(self, manipulator_id: str) -> Vector4:
        return self._positions[int(manipulator_id)]

    async def get_angles(self, manipulator_id: str) -> Vector3:
        return self._angles[int(manipulator_id)]

    async def get_shank_count(self, manipulator_id: str) -> int:
        return 1

    async def get_movement_tolerance(self) -> float:
        return 0.001

    async def set_position(self, manipulator_id: str, position: Vector4, speed: float) -> Vector4:
        self._positions[int(manipulator_id)] = position
        return position

    async def stop(self) -> None:
        pass

    async def platform_space_to_unified_space(self, platform_space: Vector4) -> Vector4:
        pass

    async def unified_space_to_platform_space(self, unified_space: Vector4) -> Vector4:
        pass
