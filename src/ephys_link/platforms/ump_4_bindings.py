from vbl_aquarium.models.unity import Vector3, Vector4

from ephys_link.util.base_bindings import BaseBindings


class Ump4Bindings(BaseBindings):
    """Bindings for UMP-4 platform"""

    async def get_manipulators(self) -> list[str]:
        pass

    async def get_num_axes(self) -> int:
        pass

    async def get_dimensions(self) -> Vector4:
        pass

    async def get_position(self, manipulator_id: str) -> Vector4:
        return Vector4()

    async def get_angles(self, manipulator_id: str) -> Vector3:
        pass

    async def get_shank_count(self, manipulator_id: str) -> int:
        pass

    async def set_position(self, manipulator_id: str, position: Vector4, speed: float) -> Vector4:
        pass

    async def calibrate(self, manipulator_id: str) -> str:
        pass

    async def stop(self) -> str:
        pass

    async def platform_space_to_unified_space(self, platform_space: Vector4) -> Vector4:
        pass

    async def unified_space_to_platform_space(self, unified_space: Vector4) -> Vector4:
        pass
