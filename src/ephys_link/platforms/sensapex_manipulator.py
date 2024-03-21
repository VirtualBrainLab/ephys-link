"""Sensapex Manipulator class

Handles logic for calling Sensapex API functions. Also includes extra logic for safe
function calls, error handling, managing per-manipulator attributes, and returning the
appropriate callback parameters like in :mod:`ephys_link.sensapex_handler`.
"""

from __future__ import annotations

import asyncio
import threading
from typing import TYPE_CHECKING

from vbl_aquarium.models.ephys_link import *
from vbl_aquarium.models.unity import Vector4

import ephys_link.common as com
from ephys_link.platform_manipulator import (
    HOURS_TO_SECONDS,
    MM_TO_UM,
    POSITION_POLL_DELAY,
    PlatformManipulator,
)

if TYPE_CHECKING:
    import socketio
    from sensapex import SensapexDevice


class SensapexManipulator(PlatformManipulator):
    """Representation of a single Sensapex manipulator

    :param device: A Sensapex device
    :type device: :class: `sensapex.SensapexDevice`
    """

    def __init__(self, device: SensapexDevice) -> None:
        """Construct a new Manipulator object

        :param device: A Sensapex device
        """
        super().__init__()
        self._device = device
        self._id = device.dev_id

    # Device functions
    def get_pos(self) -> PositionalResponse:
        """Get the current position of the manipulator and convert it into mm.

        :return: Position in (x, y, z, w) (or an empty array on error) in mm and error message (if any).
        :rtype: :class:`ephys_link.common.PositionalOutputData`
        """
        try:
            # com.dprint(f"[SUCCESS]\t Got position of manipulator {self._id}\n")
            return PositionalResponse(position=Vector4(
                **dict(zip(Vector4.model_fields.keys(), [axis / MM_TO_UM for axis in self._device.get_pos(1)]))))
        except Exception as e:
            print(f"[ERROR]\t\t Getting position of manipulator {self._id}")
            print(f"{e}\n")
            return PositionalResponse(error="Error getting position")

    async def goto_pos(self, request: GotoPositionRequest) -> PositionalResponse:
        """Move manipulator to position.

        :param request: The goto request parsed from the server.
        :type request: :class:`vbl_aquarium.models.ephys_link.GotoPositionRequest`
        :return: Resulting position in (x, y, z, w) (or an empty array on error) in mm and error message (if any).
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
                d_axis = target_position_um.w
                target_position_um = target_position_um.model_copy(
                    update={**self.get_pos().position.model_dump(), "w": d_axis})

            # Mark movement as started
            self._is_moving = True

            # Send move command
            movement = self._device.goto_pos(target_position_um, request.speed * MM_TO_UM)

            # Wait for movement to finish
            while not movement.finished:
                await asyncio.sleep(POSITION_POLL_DELAY)

            # Get position
            final_position = self.get_pos().position

            # Mark movement as finished.
            self._is_moving = False

            # Return success unless write was disabled during movement (meaning a stop occurred).
            if not self._can_write:
                com.dprint(f"[ERROR]\t\t Manipulator {self._id} movement canceled")
                return PositionalResponse(error="Manipulator movement canceled")

            # Return error if movement did not reach target.
            if not all(abs(axis) < self._movement_tolerance for axis in final_position - request.position):
                com.dprint(f"[ERROR]\t\t Manipulator {self._id} did not reach target position")
                com.dprint(f"\t\t\t Expected: {request.position}, Got: {final_position}")
                return PositionalResponse(error="Manipulator did not reach target position")

            # Made it to the target.
            com.dprint(f"[SUCCESS]\t Moved manipulator {self._id} to position {final_position}\n")
            return PositionalResponse(position=final_position)
        except Exception as e:
            print(f"[ERROR]\t\t Moving manipulator {self._id} to position {request.position}")
            print(f"{e}\n")
            return PositionalResponse(error="Error moving manipulator")

    async def drive_to_depth(self, request: DriveToDepthRequest) -> DriveToDepthResponse:
        """Drive the manipulator to a certain depth.

        :param request: The drive to depth request parsed from the server.
        :type request: :class:`vbl_aquarium.models.ephys_link.DriveToDepthRequest`
        :return: Resulting depth in mm (or 0 on error) and error message (if any).
        :rtype: :class:`ephys_link.common.DriveToDepthOutputData`
        """
        # Get position before this movement
        target_pos = self.get_pos().position

        target_pos = target_pos.model_copy(update={"w": request.depth})
        movement_result = await self.goto_pos(GotoPositionRequest(**request.model_dump(), position=target_pos))
        return DriveToDepthResponse(depth=movement_result.position.w, error=movement_result.error)

    def set_inside_brain(self, inside: bool) -> None:
        """Set if the manipulator is inside the brain.

        Used to signal that the brain should move at :const:`INSIDE_BRAIN_SPEED_LIMIT`

        :param inside: True if the manipulator is inside the brain, False otherwise.
        :type inside: bool
        :return: None
        """
        self._inside_brain = inside

    def get_can_write(self) -> bool:
        """Return if the manipulator can move.

        :return: True if the manipulator can move, False otherwise.
        :rtype: bool
        """
        return self._can_write

    def set_can_write(self, request: CanWriteRequest) -> None:
        """Set if the manipulator can move.

        :param request: The can write request parsed from the server.
        :type request: :class:`vbl_aquarium.models.ephys_link.CanWriteRequest`
        :return: None
        """
        self._can_write = request.can_write

        if request.can_write and request.hours > 0:
            if self._reset_timer:
                self._reset_timer.cancel()
            self._reset_timer = threading.Timer(request.hours * HOURS_TO_SECONDS, self.reset_can_write)
            self._reset_timer.start()

    def reset_can_write(self) -> None:
        """Reset the :attr:`can_write` flag."""
        self._can_write = False

    # Calibration
    def call_calibrate(self) -> None:
        """Calibrate the manipulator.

        :return: None
        """
        self._device.calibrate_zero_position()

    def get_calibrated(self) -> bool:
        """Return the calibration state of the manipulator.

        :return: True if the manipulator is calibrated, False otherwise.
        :rtype: bool
        """
        return self._calibrated

    def set_calibrated(self) -> None:
        """Set the manipulator to be calibrated.

        :return: None
        """
        self._calibrated = True

    def stop(self) -> None:
        """Stop the manipulator

        :return: None
        """
        self._can_write = False
        self._device.stop()
        com.dprint(f"[SUCCESS]\t Stopped manipulator {self._id}")
