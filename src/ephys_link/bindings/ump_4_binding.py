"""Bindings for Sensapex uMp-4 platform.

Usage: Instantiate Ump4Bindings to interact with the Sensapex uMp-4 platform.
"""

from asyncio import get_running_loop
from typing import NoReturn, final, override

from sensapex import UMP, SensapexDevice  # pyright: ignore [reportMissingTypeStubs]
from vbl_aquarium.models.unity import Vector4

from ephys_link.utils.base_binding import BaseBinding
from ephys_link.utils.constants import RESOURCES_DIRECTORY
from ephys_link.utils.converters import (
    list_to_vector4,
    scalar_mm_to_um,
    um_to_mm,
    vector4_to_array,
    vector_mm_to_um,
)


@final
class Ump4Binding(BaseBinding):
    """Bindings for UMP-4 platform"""

    def __init__(self) -> None:
        """Initialize UMP-4 bindings."""

        # Establish connection to Sensapex API (exit if connection fails).
        UMP.set_library_path(RESOURCES_DIRECTORY)
        self._ump = UMP.get_ump()  # pyright: ignore [reportUnknownMemberType]

    @staticmethod
    @override
    def get_display_name() -> str:
        return "Sensapex uMp-4"

    @staticmethod
    @override
    def get_cli_name() -> str:
        return "ump-4"

    @override
    async def get_manipulators(self) -> list[str]:
        return list(map(str, self._ump.list_devices()))

    @override
    async def get_axes_count(self) -> int:
        return 4

    @override
    def get_dimensions(self) -> Vector4:
        return Vector4(x=20, y=20, z=20, w=20)

    @override
    async def get_position(self, manipulator_id: str) -> Vector4:
        return um_to_mm(list_to_vector4(self._get_device(manipulator_id).get_pos(1)))  # pyright: ignore [reportUnknownMemberType]

    @override
    async def get_angles(self, manipulator_id: str) -> NoReturn:
        """uMp-4 does not support getting angles so raise an error.

        Raises:
            AttributeError: uMp-4 does not support getting angles.
        """
        error_message = "UMP-4 does not support getting angles"
        raise AttributeError(error_message)

    @override
    async def get_shank_count(self, manipulator_id: str) -> NoReturn:
        """uMp-4 does not support getting shank count so raise an error.

        Raises:
            AttributeError: uMp-4 does not support getting shank count.
        """
        error_message = "UMP-4 does not support getting shank count"
        raise AttributeError(error_message)

    @override
    def get_movement_tolerance(self) -> float:
        return 0.001

    @override
    async def set_position(self, manipulator_id: str, position: Vector4, speed: float) -> Vector4:
        # Convert position to micrometers.
        target_position_um = vector_mm_to_um(position)

        # Request movement.
        movement = self._get_device(manipulator_id).goto_pos(  # pyright: ignore [reportUnknownMemberType]
            vector4_to_array(target_position_um), scalar_mm_to_um(speed)
        )

        # Wait for movement to finish.
        _ = await get_running_loop().run_in_executor(None, movement.finished_event.wait, None)

        # Handle interrupted movement.
        if movement.interrupted:
            error_message = f"Manipulator {manipulator_id} interrupted: {movement.interrupt_reason}"  # pyright: ignore [reportUnknownMemberType]
            raise RuntimeError(error_message)

        # Handle empty end position.
        if movement.last_pos is None or len(movement.last_pos) == 0:  # pyright: ignore [reportUnknownMemberType]
            error_message = f"Manipulator {manipulator_id} did not reach target position"
            raise RuntimeError(error_message)

        return um_to_mm(list_to_vector4(movement.last_pos))  # pyright: ignore [reportArgumentType, reportUnknownMemberType]

    @override
    async def set_depth(self, manipulator_id: str, depth: float, speed: float) -> float:
        # Augment current position with depth.
        current_position = await self.get_position(manipulator_id)
        new_platform_position = current_position.model_copy(update={"w": depth})

        # Make the movement.
        final_platform_position = await self.set_position(manipulator_id, new_platform_position, speed)

        # Return the final depth.
        return float(final_platform_position.w)

    @override
    async def stop(self, manipulator_id: str) -> None:
        self._get_device(manipulator_id).stop()

    @override
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

    @override
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
        return self._ump.get_device(int(manipulator_id))  # pyright: ignore [reportUnknownMemberType]
