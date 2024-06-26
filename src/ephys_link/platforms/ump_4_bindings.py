from asyncio import get_running_loop

from sensapex import UMP, SensapexDevice
from vbl_aquarium.models.unity import Vector3, Vector4

from ephys_link.util.base_bindings import BaseBindings
from ephys_link.util.common import RESOURCES_PATH, array_to_vector4, mm_to_um, mmps_to_umps
from ephys_link.util.console import Console


class Ump4Bindings(BaseBindings):
    """Bindings for UMP-4 platform"""

    def __init__(self) -> None:
        """Initialize UMP-4 bindings."""
        super().__init__()

        # Establish connection to Sensapex API (exit if connection fails).
        UMP.set_library_path(RESOURCES_PATH)
        self._ump = UMP.get_ump()
        if self._ump is None:
            error_message = "Unable to connect to uMp"
            Console.error_print(error_message)
            raise ValueError(error_message)

    async def get_manipulators(self) -> list[str]:
        return list(map(str, self._ump.list_devices()))

    async def get_num_axes(self) -> int:
        return 4

    async def get_dimensions(self) -> Vector4:
        return Vector4(x=20, y=20, z=20, w=20)

    async def get_position(self, manipulator_id: str) -> Vector4:
        return array_to_vector4(self._get_device(manipulator_id).get_pos(1))

    async def get_angles(self, manipulator_id: str) -> Vector3:
        """uMp-4 does not support getting angles so raise an error.

        :raises: AttributeError
        """
        error_message = "UMP-4 does not support getting angles"
        raise AttributeError(error_message)

    async def get_shank_count(self, manipulator_id: str) -> int:
        """uMp-4 does not support getting shank count so raise an error.

        :raises: AttributeError
        """
        error_message = "UMP-4 does not support getting shank count"
        raise AttributeError(error_message)

    async def get_movement_tolerance(self) -> float:
        return 0.001

    async def set_position(self, manipulator_id: str, position: Vector4, speed: float) -> Vector4:
        """Set the position of the manipulator.

        Waits using Asyncio until the movement is finished. This assumes the application is running in an event loop.

        :param manipulator_id: Manipulator ID.
        :type manipulator_id: str
        :param position: Platform space position to set the manipulator to (mm).
        :type position: Vector4
        :param speed: Speed to move the manipulator to the position (mm/s).
        :type speed: float
        :returns: Final position of the manipulator in platform space (mm).
        :rtype: Vector4
        :raises RuntimeError: If the movement is interrupted.
        """
        # Convert position to micrometers.
        target_position_um = mm_to_um(position)

        # Request movement.
        movement = self._get_device(manipulator_id).goto_pos(target_position_um, mmps_to_umps(speed))

        # Wait for movement to finish.
        await get_running_loop().run_in_executor(None, movement.finished_event.wait)

        # Handle interrupted movement.
        if movement.interrupted:
            error_message = f"Manipulator {manipulator_id} interrupted: {movement.interrupt_reason}"
            raise RuntimeError(error_message)

        return array_to_vector4(movement.final_pos)

    async def stop(self) -> None:
        for device_ids in await self.get_manipulators():
            self._get_device(device_ids).stop()

    async def platform_space_to_unified_space(self, platform_space: Vector4) -> Vector4:
        # unified   <-  platform
        # +x        <-  +y
        # +y        <-  -z
        # +z        <-  +x
        # +d        <-  +d

        return Vector4(
            x=platform_space.y,
            y=(await self.get_dimensions()).z - platform_space.z,
            z=platform_space.x,
            w=platform_space.w,
        )

    async def unified_space_to_platform_space(self, unified_space: Vector4) -> Vector4:
        # platform  <-  unified
        # +x        <-  +z
        # +y        <-  +x
        # +z        <-  -y
        # +d        <-  +d

        return Vector4(
            x=unified_space.z,
            y=unified_space.x,
            z=(await self.get_dimensions()).z - unified_space.y,
            w=unified_space.w,
        )

    # Helper methods.
    def _get_device(self, manipulator_id: str) -> SensapexDevice:
        return self._ump.get_device(int(manipulator_id))
