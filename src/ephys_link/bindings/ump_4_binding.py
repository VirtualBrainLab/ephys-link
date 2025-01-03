"""Bindings for Sensapex uMp-4 platform.

Usage: Instantiate Ump4Bindings to interact with the Sensapex uMp-4 platform.
"""

from asyncio import get_running_loop

from sensapex import UMP, SensapexDevice
from vbl_aquarium.models.unity import Vector3, Vector4

from ephys_link.utils.base_binding import BaseBinding
from ephys_link.utils.common import (
    RESOURCES_DIRECTORY,
    array_to_vector4,
    scalar_mm_to_um,
    um_to_mm,
    vector4_to_array,
    vector_mm_to_um,
)


class Ump4Binding(BaseBinding):
    """Bindings for UMP-4 platform"""

    def __init__(self) -> None:
        """Initialize UMP-4 bindings."""

        # Establish connection to Sensapex API (exit if connection fails).
        UMP.set_library_path(RESOURCES_DIRECTORY)
        self._ump = UMP.get_ump()
        if self._ump is None:
            error_message = "Unable to connect to uMp"
            raise ValueError(error_message)

    async def get_manipulators(self) -> list[str]:
        return list(map(str, self._ump.list_devices()))

    async def get_axes_count(self) -> int:
        return 4

    def get_dimensions(self) -> Vector4:
        return Vector4(x=20, y=20, z=20, w=20)

    async def get_position(self, manipulator_id: str) -> Vector4:
        return um_to_mm(array_to_vector4(self._get_device(manipulator_id).get_pos(1)))

    # noinspection PyTypeChecker
    async def get_angles(self, _: str) -> Vector3:
        """uMp-4 does not support getting angles so raise an error.

        Raises:
            AttributeError: uMp-4 does not support getting angles.
        """
        error_message = "UMP-4 does not support getting angles"
        raise AttributeError(error_message)

    # noinspection PyTypeChecker
    async def get_shank_count(self, _: str) -> int:
        """uMp-4 does not support getting shank count so raise an error.

        Raises:
            AttributeError: uMp-4 does not support getting shank count.
        """
        error_message = "UMP-4 does not support getting shank count"
        raise AttributeError(error_message)

    def get_movement_tolerance(self) -> float:
        return 0.001

    # noinspection DuplicatedCode
    async def set_position(self, manipulator_id: str, position: Vector4, speed: float) -> Vector4:
        # Convert position to micrometers.
        target_position_um = vector_mm_to_um(position)

        # Request movement.
        movement = self._get_device(manipulator_id).goto_pos(
            vector4_to_array(target_position_um), scalar_mm_to_um(speed)
        )

        # Wait for movement to finish.
        await get_running_loop().run_in_executor(None, movement.finished_event.wait, None)

        # Handle interrupted movement.
        if movement.interrupted:
            error_message = f"Manipulator {manipulator_id} interrupted: {movement.interrupt_reason}"
            raise RuntimeError(error_message)

        return um_to_mm(array_to_vector4(movement.last_pos))

    async def set_depth(self, manipulator_id: str, depth: float, speed: float) -> float:
        # Augment current position with depth.
        current_position = await self.get_position(manipulator_id)
        new_platform_position = current_position.model_copy(update={"w": depth})

        # Make the movement.
        final_platform_position = await self.set_position(manipulator_id, new_platform_position, speed)

        # Return the final depth.
        return float(final_platform_position.w)

    async def stop(self, manipulator_id: str) -> None:
        self._get_device(manipulator_id).stop()

    def platform_space_to_unified_space(self, platform_space: Vector4) -> Vector4:
        # unified   <-  platform
        # +x        <-  +y
        # +y        <-  -z
        # +z        <-  +x
        # +d        <-  +d

        return Vector4(
            x=platform_space.y,
            y=self.get_dimensions().z - platform_space.z,
            z=platform_space.x,
            w=platform_space.w,
        )

    def unified_space_to_platform_space(self, unified_space: Vector4) -> Vector4:
        # platform  <-  unified
        # +x        <-  +z
        # +y        <-  +x
        # +z        <-  -y
        # +d        <-  +d

        return Vector4(
            x=unified_space.z,
            y=unified_space.x,
            z=self.get_dimensions().z - unified_space.y,
            w=unified_space.w,
        )

    # Helper methods.
    def _get_device(self, manipulator_id: str) -> SensapexDevice:
        return self._ump.get_device(int(manipulator_id))
