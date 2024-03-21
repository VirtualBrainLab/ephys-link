"""New Scale Manipulator class

Handles logic for calling New Scale API functions. Also includes extra logic for safe
function calls, error handling, managing per-manipulator attributes, and returning the
appropriate callback parameters like in :mod:`ephys_link.new_scale_handler`.
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

    # noinspection PyUnresolvedReferences
    from NstMotorCtrl import NstCtrlAxis

# Constants
ACCELERATION_MULTIPLIER = 5
CUTOFF_MULTIPLIER = 0.005
AT_TARGET_FLAG = 0x040000


class NewScaleManipulator(PlatformManipulator):
    def __init__(
            self,
            manipulator_id: str,
            x_axis: NstCtrlAxis,
            y_axis: NstCtrlAxis,
            z_axis: NstCtrlAxis,
    ) -> None:
        """Construct a new Manipulator object

        :param manipulator_id: Manipulator ID
        :param x_axis: X axis object
        :param y_axis: Y axis object
        :param z_axis: Z axis object
        """

        super().__init__()
        self._id = manipulator_id
        self._movement_tolerance = 0.01
        self._x = x_axis
        self._y = y_axis
        self._z = z_axis
        self._axes = [self._x, self._y, self._z]

        # Set to CL control
        self._x.SetCL_Enable(True)
        self._y.SetCL_Enable(True)
        self._z.SetCL_Enable(True)

    def query_all_axes(self):
        """Query all axes for their position and status"""
        for axis in self._axes:
            axis.QueryPosStatus()

    def get_pos(self) -> PositionalResponse:
        """Get the current position of the manipulator and convert it into mm.

        :return: Position of manipulator in (x, y, z, z) in mm (or an empty array on error) and error message (if any).
        :rtype: :class:`ephys_link.common.PositionalOutputData`
        """
        self.query_all_axes()

        # Get position data and convert from µm to mm
        try:
            # com.dprint(f"[SUCCESS]\t Got position of manipulator {self._id}\n")
            return PositionalResponse(
                position=Vector4(x=self._x.CurPosition / MM_TO_UM, y=self._y.CurPosition / MM_TO_UM,
                                 z=self._z.CurPosition / MM_TO_UM, w=self._z.CurPosition / MM_TO_UM))
        except Exception as e:
            print(f"[ERROR]\t\t Getting position of manipulator {self._id}")
            print(f"{e}\n")
            return PositionalResponse(error="Error getting position")

    async def goto_pos(self, request: GotoPositionRequest) -> PositionalResponse:
        """Move manipulator to position.

        :param request: The goto request parsed from the server.
        :type request: :class:`vbl_aquarium.models.ephys_link.GotoPositionRequest`
        :return: Resulting position of manipulator in (x, y, z, z) in mm (or an empty array on error)
         and error message (if any).
        :rtype: :class:`ephys_link.common.PositionalOutputData`
        """
        # Check if able to write
        if not self._can_write:
            print(f"[ERROR]\t\t Manipulator {self._id} movement canceled")
            return PositionalResponse(error="Manipulator movement canceled")

        # Stop current movement
        if self._is_moving:
            for axis in self._axes:
                axis.Stop()
            self._is_moving = False

        try:
            target_position_um = request.position * MM_TO_UM

            # Restrict target position to just z-axis if inside brain
            if self._inside_brain:
                z_axis = target_position_um.z
                target_position_um = target_position_um.model_copy(
                    update={**self.get_pos().position.model_dump(), "z": z_axis})

            # Mark movement as started
            self._is_moving = True

            # Send move command
            speed_um = request.speed * MM_TO_UM
            for i in range(3):
                self._axes[i].SetCL_Speed(
                    speed_um,
                    speed_um * ACCELERATION_MULTIPLIER,
                    speed_um * CUTOFF_MULTIPLIER,
                )
                self._axes[i].MoveAbsolute(target_position_um[i])

            # Check and wait for completion (while able to write)
            self.query_all_axes()
            while (
                    not (self._x.CurStatus & AT_TARGET_FLAG)
                    or not (self._y.CurStatus & AT_TARGET_FLAG)
                    or not (self._z.CurStatus & AT_TARGET_FLAG)
            ) and self._can_write:
                await asyncio.sleep(POSITION_POLL_DELAY)
                self.query_all_axes()

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
                com.dprint(f"[ERROR]\t\t Manipulator {self._id} did not reach target position.")
                com.dprint(f"\t\t\t Expected: {request.position}, Got: {final_position}")
                return PositionalResponse(error="Manipulator did not reach target position")

            # Made it to the target.
            com.dprint(f"[SUCCESS]\t Moved manipulator {self._id} to position" f" {final_position}\n")
            return PositionalResponse(position=final_position)
        except Exception as e:
            print(f"[ERROR]\t\t Moving manipulator {self._id} to position {request.position}")
            print(f"{e}\n")
            return PositionalResponse(error="Error moving manipulator")

    async def drive_to_depth(self, request: DriveToDepthRequest) -> DriveToDepthResponse:
        """Drive the manipulator to a certain depth.

        :param request: The drive to depth request parsed from the server.
        :type request: :class:`vbl_aquarium.models.ephys_link.DriveToDepthRequest`
        :return: Resulting depth of manipulator in mm (or 0 on error) and error message (if any).
        :rtype: :class:`ephys_link.common.DriveToDepthOutputData`
        """
        # Check if able to write
        if not self._can_write:
            print(f"[ERROR]\t\t Manipulator {self._id} movement canceled")
            return DriveToDepthResponse(error="Manipulator movement canceled")

        # Stop current movement
        if self._is_moving:
            for axis in self._axes:
                axis.Stop()
            self._is_moving = False

        try:
            target_depth_um = request.depth * MM_TO_UM

            # Mark movement as started
            self._is_moving = True

            # Send move command to just z axis
            speed_um = request.speed * MM_TO_UM
            self._z.SetCL_Speed(
                speed_um,
                speed_um * ACCELERATION_MULTIPLIER,
                speed_um * CUTOFF_MULTIPLIER,
            )
            self._z.MoveAbsolute(target_depth_um)

            # Check and wait for completion (while able to write)
            self._z.QueryPosStatus()
            while not (self._z.CurStatus & AT_TARGET_FLAG) and self._can_write:
                await asyncio.sleep(0.1)
                self._z.QueryPosStatus()

            # Get position
            final_depth = self.get_pos().position.w

            # Mark movement as finished
            self._is_moving = False

            # Return success unless write was disabled during movement (meaning a stop occurred)
            if not self._can_write:
                com.dprint(f"[ERROR]\t\t Manipulator {self._id} movement canceled")
                return DriveToDepthResponse(error="Manipulator movement canceled")

            # Return error if movement did not reach target.
            if not abs(final_depth - request.depth) < self._movement_tolerance:
                com.dprint(f"[ERROR]\t\t Manipulator {self._id} did not reach target depth")
                com.dprint(f"\t\t\t Expected: {request.depth}, Got: {final_depth}")
                return DriveToDepthResponse(error="Manipulator did not reach target depth")

            # Made it to the target.
            com.dprint(f"[SUCCESS]\t Moved manipulator {self._id} to position" f" {final_depth}\n")
            return DriveToDepthResponse(depth=final_depth)
        except Exception as e:
            print(f"[ERROR]\t\t Moving manipulator {self._id} to depth {request.depth}")
            print(f"{e}\n")
            # Return 0 and error message on failure
            return DriveToDepthResponse(error="Error driving manipulator")

    def calibrate(self) -> bool:
        """Calibrate the manipulator.

        :return: None
        """
        return self._x.CalibrateFrequency() and self._y.CalibrateFrequency() and self._z.CalibrateFrequency()

    def get_calibrated(self) -> bool:
        """Return the calibration state of the manipulator.

        :return: True if the manipulator is calibrated, False otherwise.
        :rtype: bool
        """
        return self._calibrated

    def set_calibrated(self) -> None:
        """Set the manipulator to calibrated

        :return: None
        """
        self._calibrated = True

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

    def get_can_write(self) -> bool:
        """Return if the manipulator can move.

        :return: True if the manipulator can move, False otherwise.
        :rtype: bool
        """
        return self._can_write

    def set_inside_brain(self, inside: bool) -> None:
        """Set if the manipulator is inside the brain.

        :param inside: True if the manipulator is inside the brain, False otherwise.
        :type inside: bool
        :return: None
        """
        self._inside_brain = inside

    def stop(self) -> None:
        """Stop all axes on manipulator.

        :returns None
        """
        for axis in self._axes:
            axis.Stop()
        self._can_write = False
        com.dprint(f"[SUCCESS]\t Stopped manipulator {self._id}\n")
