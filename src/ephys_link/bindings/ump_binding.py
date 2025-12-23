"""Bindings for Sensapex uMp platform.

Usage: Instantiate UmpBindings to interact with Sensapex uMp-4 and uMp-3 manipulators.
"""

from asyncio import get_running_loop
from typing import NoReturn, final, override

from sensapex import UMP, SensapexDevice  # pyright: ignore [reportMissingTypeStubs]
from vbl_aquarium.models.unity import Vector4

from ephys_link.utils.base_binding import BaseBinding
from ephys_link.utils.converters import (
    list_to_vector4,
    scalar_mm_to_um,
    um_to_mm,
    vector4_to_array,
    vector_mm_to_um,
)


@final
class UmpBinding(BaseBinding):
    """Bindings for uMp platform"""

    # Number of axes for uMp-3.
    UMP_3_NUM_AXES = 3

    def __init__(self) -> None:
        """Initialize uMp bindings."""

        # Establish connection to Sensapex API (exit if connection fails).
        self._ump: UMP = UMP.get_ump()  # pyright: ignore [reportUnknownMemberType]

        # Compute axis count, assumed as the first device. 0 if no devices are connected.
        device_ids = list(map(str, self._ump.list_devices()))
        self.axis_count: int = 0 if len(device_ids) == 0 else self._get_device(device_ids[0]).n_axes()

    @staticmethod
    @override
    def get_display_name() -> str:
        return "Sensapex uMp"

    @staticmethod
    @override
    def get_cli_name() -> str:
        return "ump"

    @override
    async def get_manipulators(self) -> list[str]:
        device_ids = list(map(str, self._ump.list_devices()))

        # Currently only supports using uMp-4 XOR uMp-3. Throw error if both are connected.
        if any(self._get_device(device_id).n_axes() != self.axis_count for device_id in device_ids):  # pyright: ignore [reportUnknownArgumentType]
            msg = "uMp-4 and uMp-3 cannot be used at the same time."
            raise RuntimeError(msg)

        return device_ids

    @override
    async def get_axes_count(self) -> int:
        return self.axis_count

    @override
    def get_dimensions(self) -> Vector4:
        return Vector4(x=20, y=20, z=20, w=20)

    @override
    async def get_position(self, manipulator_id: str) -> Vector4:
        # Get the position list from the device.
        position = self._get_device(manipulator_id).get_pos(1)  # pyright: ignore [reportUnknownMemberType]

        # Copy x-coordinate into depth for uMp-3.
        return um_to_mm(list_to_vector4([*position, position[0]] if self._is_ump_3() else position))

    @override
    async def get_angles(self, manipulator_id: str) -> NoReturn:
        """uMp does not support getting angles so raise an error.

        Raises:
            AttributeError: uMp does not support getting angles.
        """
        error_message = "uMp does not support getting angles"
        raise AttributeError(error_message)

    @override
    async def get_shank_count(self, manipulator_id: str) -> NoReturn:
        """uMp does not support getting shank count so raise an error.

        Raises:
            AttributeError: uMp does not support getting shank count.
        """
        error_message = "uMp does not support getting shank count"
        raise AttributeError(error_message)

    @staticmethod
    @override
    def get_movement_tolerance() -> float:
        return 0.001

    @override
    async def set_position(self, manipulator_id: str, position: Vector4, speed: float) -> Vector4:
        # Convert position to micrometers array.
        target_position_um = vector4_to_array(vector_mm_to_um(position))

        # Request movement (clip 4th axis for uMp-3).
        movement = self._get_device(
            manipulator_id
        ).goto_pos(  # pyright: ignore [reportUnknownMemberType]
            target_position_um[: self.UMP_3_NUM_AXES] if self._is_ump_3() else target_position_um,
            scalar_mm_to_um(speed),
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

        return um_to_mm(
            list_to_vector4([*movement.last_pos, movement.last_pos[0]] if self._is_ump_3() else list(movement.last_pos))  # pyright: ignore [reportUnknownArgumentType, reportUnknownMemberType]
        )

    @override
    async def set_depth(self, manipulator_id: str, depth: float, speed: float) -> float:
        # Augment current position with depth.
        current_position = await self.get_position(manipulator_id)
        new_platform_position = current_position.model_copy(update={"x" if self._is_ump_3() else "w": depth})

        # Make the movement.
        final_platform_position = await self.set_position(manipulator_id, new_platform_position, speed)

        # Return the final depth.
        return float(final_platform_position.w)

    @override
    async def stop(self, manipulator_id: str) -> None:
        self._get_device(manipulator_id).stop() # pyright: ignore [reportUnknownMemberType]

    @override
    def platform_space_to_unified_space(self, platform_space: Vector4) -> Vector4:
        """
        For uMp-3:
        unified   <-  platform
        +x        <-  +y
        +y        <-  -x
        +z        <-  -z
        +d        <-  +d

        For uMp-4:
        unified   <-  platform
        +x        <-  +y
        +y        <-  -z
        +z        <-  +x
        +d        <-  +d
        """

        return (
            Vector4(
                x=platform_space.y,
                y=self.get_dimensions().x - platform_space.x,
                z=self.get_dimensions().z - platform_space.z,
                w=platform_space.w,
            )
            if self._is_ump_3()
            else Vector4(
                x=platform_space.y,
                y=self.get_dimensions().z - platform_space.z,
                z=platform_space.x,
                w=platform_space.w,
            )
        )

    @override
    def unified_space_to_platform_space(self, unified_space: Vector4) -> Vector4:
        """
        For uMp-3:
        platform  <-  unified
        +x        <-  -y
        +y        <-  +x
        +z        <-  -z
        +d        <-  +d

        For uMp-4:
        platform  <-  unified
        +x        <-  +z
        +y        <-  +x
        +z        <-  -y
        +d        <-  +d
        """

        return (
            Vector4(
                x=self.get_dimensions().y - unified_space.y,
                y=unified_space.x,
                z=self.get_dimensions().z - unified_space.z,
                w=unified_space.w,
            )
            if self._is_ump_3()
            else Vector4(
                x=unified_space.z,
                y=unified_space.x,
                z=self.get_dimensions().y - unified_space.y,
                w=unified_space.w,
            )
        )

    # Helper methods.
    def _get_device(self, manipulator_id: str) -> SensapexDevice:
        """Returns the Sensapex device object for the given manipulator ID.

        Args:
            manipulator_id: Manipulator ID.
        Returns:
            Sensapex device object.
        """

        return self._ump.get_device(int(manipulator_id))  # pyright: ignore [reportUnknownMemberType]

    def _is_ump_3(self) -> bool:
        """Check if the current device is uMp-3.

        Returns:
            True if the device is uMp-3, False otherwise.
        """
        return self.axis_count == self.UMP_3_NUM_AXES
