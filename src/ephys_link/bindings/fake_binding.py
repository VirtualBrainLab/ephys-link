from vbl_aquarium.models.unity import Vector3, Vector4

from ephys_link.utils.base_binding import BaseBinding
from ephys_link.utils.common import array_to_vector4


class FakeBinding(BaseBinding):
    def __init__(self, *args, **kwargs) -> None:
        """Initialize fake manipulator infos."""

        super().__init__(*args, **kwargs)
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

    @staticmethod
    def get_display_name() -> str:
        return "Fake Manipulator"

    @staticmethod
    def get_cli_name() -> str:
        return "fake"

    async def get_manipulators(self) -> list[str]:
        return list(map(str, range(8)))

    async def get_axes_count(self) -> int:
        return 4

    def get_dimensions(self) -> Vector4:
        return array_to_vector4([20] * 4)

    async def get_position(self, manipulator_id: str) -> Vector4:
        return self._positions[int(manipulator_id)]

    async def get_angles(self, manipulator_id: str) -> Vector3:
        return self._angles[int(manipulator_id)]

    async def get_shank_count(self, _: str) -> int:
        return 1

    def get_movement_tolerance(self) -> float:
        return 0.001

    async def set_position(self, manipulator_id: str, position: Vector4, _: float) -> Vector4:
        self._positions[int(manipulator_id)] = position
        return position

    async def set_depth(self, manipulator_id: str, depth: float, _: float) -> float:
        self._positions[int(manipulator_id)].w = depth
        return depth

    async def stop(self, _: str) -> None:
        pass

    def platform_space_to_unified_space(self, platform_space: Vector4) -> Vector4:
        pass

    def unified_space_to_platform_space(self, unified_space: Vector4) -> Vector4:
        pass
