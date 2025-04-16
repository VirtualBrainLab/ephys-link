"""Bindings for Sensapex uMp-3 platform.

Usage: Instantiate Ump3Bindings to interact with the Sensapex uMp-3 platform.
"""

from asyncio import get_running_loop
from typing import NoReturn, final, override

from numpy import concatenate
from vbl_aquarium.models.unity import Vector4

from ephys_link.bindings.ump_4_binding import Ump4Binding
from ephys_link.utils.converters import list_to_vector4, scalar_mm_to_um, um_to_mm, vector4_to_array, vector_mm_to_um


@final
class Ump3Binding(Ump4Binding):
    """Bindings for uMp-3 platform.

    Most functionality is identical to uMp-4 so we inherit from it.
    """

    @staticmethod
    @override
    def get_display_name() -> str:
        return "Sensapex uMp-3"

    @staticmethod
    @override
    def get_cli_name() -> str:
        return "ump-3"

    @override
    async def get_axes_count(self) -> int:
        return 3

    @override
    async def get_position(self, manipulator_id: str) -> Vector4:
        """Get the position of the manipulator.

        Repeats the x-coordinate into the depth coordinate to make it 4D.
        """
        three_axis_position = self._get_device(manipulator_id).get_pos(1)
        return um_to_mm(list_to_vector4([*three_axis_position, three_axis_position[0]]))  # pyright: ignore [reportUnknownMemberType]

    @override
    async def get_angles(self, manipulator_id: str) -> NoReturn:
        """uMp-3 does not support getting angles so raise an error.

        Raises:
            AttributeError: uMp-3 does not support getting angles.
        """
        error_message = "UMP-3 does not support getting angles"
        raise AttributeError(error_message)

    @override
    async def get_shank_count(self, manipulator_id: str) -> NoReturn:
        """uMp-3 does not support getting shank count so raise an error.

        Raises:
            AttributeError: uMp-3 does not support getting shank count.
        """
        error_message = "UMP-3 does not support getting shank count"
        raise AttributeError(error_message)

    @override
    async def set_position(self, manipulator_id: str, position: Vector4, speed: float) -> Vector4:
        # Convert position to micrometers.
        target_position_um = vector_mm_to_um(position)

        # Request movement (only pass in first 3 elements of target).
        movement = self._get_device(
            manipulator_id
        ).goto_pos(  # pyright: ignore [reportUnknownMemberType]
            vector4_to_array(target_position_um)[:3], scalar_mm_to_um(speed)
        )

        # Wait for movement to finish.
        _ = await get_running_loop().run_in_executor(None, movement.finished_event.wait, None)

        # Handle interrupted movement.
        if movement.interrupted:
            error_message = f"Manipulator {manipulator_id} interrupted: {movement.interrupt_reason}"  # pyright: ignore [reportUnknownMemberType]
            raise RuntimeError(error_message)

        # Handle empty end position.
        if movement.last_pos is None or len(movement.last_pos) == 0:  # pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
            error_message = f"Manipulator {manipulator_id} did not reach target position"
            raise RuntimeError(error_message)

        # Return the final position (copy x to depth).
        return um_to_mm(list_to_vector4(list(concatenate([movement.last_pos, [movement.last_pos[0]]]))))  # pyright: ignore [reportArgumentType, reportUnknownMemberType]

    @override
    async def set_depth(self, manipulator_id: str, depth: float, speed: float) -> float:
        # Augment current position with depth.
        current_position = await self.get_position(manipulator_id)
        new_platform_position = current_position.model_copy(update={"x": depth})

        # Make the movement.
        final_platform_position = await self.set_position(manipulator_id, new_platform_position, speed)

        # Return the final depth.
        return float(final_platform_position.w)

    @override
    def platform_space_to_unified_space(self, platform_space: Vector4) -> Vector4:
        # unified   <-  platform
        # +x        <-  +y
        # +y        <-  -x
        # +z        <-  -z
        # +d        <-  +d

        return Vector4(
            x=platform_space.y,
            y=self.get_dimensions().x - platform_space.x,
            z=self.get_dimensions().z - platform_space.z,
            w=platform_space.w,
        )

    @override
    def unified_space_to_platform_space(self, unified_space: Vector4) -> Vector4:
        # platform  <-  unified
        # +x        <-  -y
        # +y        <-  +x
        # +z        <-  -z
        # +d        <-  +d

        return Vector4(
            x=self.get_dimensions().y - unified_space.y,
            y=unified_space.x,
            z=self.get_dimensions().z - unified_space.z,
            w=unified_space.w,
        )
