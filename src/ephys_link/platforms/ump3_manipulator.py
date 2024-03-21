"""Sensapex uMp-3 Manipulator class

Extends from :class:`ephys_link.platforms.sensapex_manipulator.SensapexManipulator` to support the uMp-3 manipulator.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from vbl_aquarium.models.ephys_link import PositionalResponse, GotoPositionRequest
from vbl_aquarium.models.unity import Vector4

import ephys_link.common as com
from ephys_link.platform_manipulator import (
    MM_TO_UM,
    POSITION_POLL_DELAY,
)
from ephys_link.platforms.sensapex_manipulator import SensapexManipulator

if TYPE_CHECKING:
    from sensapex import SensapexDevice


class UMP3Manipulator(SensapexManipulator):
    """Representation of a single Sensapex manipulator

    :param device: A Sensapex device
    :type device: :class: `sensapex.SensapexDevice`
    """

    def __init__(self, device: SensapexDevice) -> None:
        """Construct a new Manipulator object

        :param device: A Sensapex device
        """
        super().__init__(device)

    # Device functions
    def get_pos(self) -> PositionalResponse:
        """Get the current position of the manipulator and convert it into mm.

        :return: Position in (x, y, z, x) (or an empty array on error) in mm and error message (if any).
        :rtype: :class:`ephys_link.common.PositionalOutputData`
        """
        try:
            position = [axis / MM_TO_UM for axis in self._device.get_pos(1)]
            
            # Add the depth axis to the end of the position.
            position.append(position[0])

            # com.dprint(f"[SUCCESS]\t Got position of manipulator {self._id}\n")
            return PositionalResponse(position=Vector4(**dict(zip(Vector4.model_fields.keys(), position))))
        except Exception as e:
            print(f"[ERROR]\t\t Getting position of manipulator {self._id}")
            print(f"{e}\n")
            return PositionalResponse(error="Error getting position")

    async def goto_pos(self, request: GotoPositionRequest) -> PositionalResponse:
        """Move manipulator to position.

        :param request: The goto request parsed from the server.
        :type request: :class:`vbl_aquarium.models.ephys_link.GotoPositionRequest`
        :return: Resulting position in (x, y, z, x) (or an empty array on error) in mm and error message (if any).
        :rtype: :class:`ephys_link.common.PositionalOutputData`
        """
        # Check if able to write
        if not self._can_write:
            print(f"[ERROR]\t\t Manipulator {self._id} movement canceled")
            return PositionalResponse(error="Manipulator movement canceled")

        # Stop current movement
        if self._is_moving:
            self._device.stop()
            self._is_moving = False

        try:
            target_position_um = request.position * MM_TO_UM

            # Restrict target position to just depth-axis if inside brain
            if self._inside_brain:
                d_axis = target_position_um.x
                target_position_um = target_position_um.model_copy(
                    update={**self.get_pos().position.model_dump(), "x": d_axis})

            # Mark movement as started
            self._is_moving = True

            # Send move command
            movement = self._device.goto_pos(target_position_um, request.speed * MM_TO_UM)

            # Wait for movement to finish
            while not movement.finished:
                await asyncio.sleep(POSITION_POLL_DELAY)

            # Get position
            final_position = self.get_pos().position

            # Mark movement as finished
            self._is_moving = False

            # Return success unless write was disabled during movement (meaning a stop occurred)
            if not self._can_write:
                com.dprint(f"[ERROR]\t\t Manipulator {self._id} movement canceled")
                return PositionalResponse(error="Manipulator movement canceled")

            # Return error if movement did not reach target.
            if not all(abs(axis) < self._movement_tolerance for axis in final_position - request.position):
                com.dprint(f"[ERROR]\t\t Manipulator {self._id} did not reach target position")
                com.dprint(f"\t\t\t Expected: {request.position}, Got: {final_position}")
                return PositionalResponse(error="Manipulator did not reach target position")

            # Made it to the target.
            com.dprint(f"[SUCCESS]\t Moved manipulator {self._id} to position" f" {final_position}\n")
            return PositionalResponse(position=final_position)
        except Exception as e:
            print(f"[ERROR]\t\t Moving manipulator {self._id} to position {request.position}")
            print(f"{e}\n")
            return PositionalResponse(error="Error moving manipulator")

    async def drive_to_depth(self, depth: float, speed: float) -> com.DriveToDepthOutputData:
        """Drive the manipulator to a certain depth.

        :param depth: The depth to drive to in mm.
        :type depth: float
        :param speed: The speed to drive at in mm/s.
        :type speed: float
        :return: Resulting depth in mm (or 0 on error) and error message (if any).
        :rtype: :class:`ephys_link.common.DriveToDepthOutputData`
        """
        # Get position before this movement
        target_pos = self.get_pos()["position"]

        target_pos[0] = depth
        movement_result = await self.goto_pos(target_pos, speed)

        if movement_result["error"] == "":
            # Return depth on success
            return com.DriveToDepthOutputData(movement_result["position"][3], "")

        # Return 0 and error message on failure
        return com.DriveToDepthOutputData(0, "Error driving " "manipulator")
