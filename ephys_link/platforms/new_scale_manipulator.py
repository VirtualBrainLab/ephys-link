"""New Scale Manipulator class

Handles logic for calling New Scale API functions. Also includes extra logic for safe
function calls, error handling, managing per-manipulator attributes, and returning the
appropriate callback parameters like in :mod:`ephys_link.new_scale_handler`.
"""

import asyncio
# noinspection PyUnresolvedReferences
from NstMotorCtrl import NstCtrlAxis
import ephys_link.common as com
from collections import deque
import threading

# noinspection PyPackageRequirements
import socketio


class NewScaleManipulator:
    def __init__(self, manipulator_id: str, x_axis: NstCtrlAxis, y_axis: NstCtrlAxis, z_axis: NstCtrlAxis) -> None:
        """Construct a new Manipulator object

        :param manipulator_id: Manipulator ID
        :param x_axis: X axis object
        :param y_axis: Y axis object
        :param z_axis: Z axis object
        """

        self._id = manipulator_id
        self._x = x_axis
        self._y = y_axis
        self._z = z_axis
        self._calibrated = False
        self._inside_brain = False
        self._can_write = False
        self._reset_timer = None
        self._move_queue = deque()

    class Movement:
        """Movement data struct

        :param event: An asyncio event which fires upon completion of movement
        :type event: :class: `asyncio.Event`
        :param position: A tuple of floats (x, y, z, w) representing the position to
            move to in µm
        :type position: list[float]
        """

        def __init__(self, event: asyncio.Event, position: list[float]) -> None:
            """Construct a new Movement object"""
            self.event = event
            self.position = position

    def get_pos(self) -> com.PositionalOutputData:
        """Get the current position of the manipulator and convert it into mm

        :return: Callback parameters (position in (x, y, z, 0) (or an empty array on
            error), error message)
        :rtype: :class:`ephys_link.common.PositionalOutputData`
        """
        # Query position data
        self._x.QueryPosStatus()
        self._y.QueryPosStatus()
        self._z.QueryPosStatus()

        # Get position data
        try:
            position = [self._x.CurPosition / 1000, self._y.CurPosition / 1000, self._z.CurPosition / 1000, 0]
            com.dprint(f"[SUCCESS]\t Got position of manipulator {self._id}\n")
            return com.PositionalOutputData(position, "")
        except Exception as e:
            print(f"[ERROR]\t\t Getting position of manipulator {self._id}")
            print(f"{e}\n")
            return com.PositionalOutputData([], "Error getting position")

    async def goto_pos(
            self, position: list[float], speed: float
    ) -> com.PositionalOutputData:
        """Move manipulator to position

        :param position: The position to move to
        :type position: list[float]
        :param speed: The speed to move at (in µm/s)
        :type speed: float
        :return: Callback parameters (position in (x, y, z, w) (or an empty array on
            error), error message)
        :rtype: :class:`ephys_link.common.PositionalOutputData`
        """
        # Convert position to µm
        position = [axis * 1000 for axis in position]

        # Add movement to queue
        self._move_queue.appendleft(self.Movement(asyncio.Event(), position))

        # Wait for preceding movement to finish
        if len(self._move_queue) > 1:
            await self._move_queue[1].event.wait()

        if not self._can_write:
            print(f"[ERROR]\t\t Manipulator {self._id} movement " f"canceled")
            return com.PositionalOutputData([], "Manipulator " "movement canceled")

        try:
            target_position = position
            target_speed = speed

            # Alter target position if inside brain
            if self._inside_brain:
                target_position = self.get_pos()["position"]
                target_position[3] = position[3]

            # Move manipulator
            x_movement = self._x.MoveAbsolute(target_position[0])
            y_movement = self._y.MoveAbsolute(target_position[1])
            z_movement = self._z.MoveAbsolute(target_position[2])

            # Wait for movement to finish
            while not x_movement and y_movement and z_movement:
                await asyncio.sleep(0.1)

            # Get position
            manipulator_final_position = self.get_pos()["position"]

            # Remove event from queue and mark as completed
            self._move_queue.pop().event.set()

            com.dprint(
                f"[SUCCESS]\t Moved manipulator {self._id} to position"
                f" {manipulator_final_position}\n"
            )
            return com.PositionalOutputData(manipulator_final_position, "")
        except Exception as e:
            print(
                f"[ERROR]\t\t Moving manipulator {self._id} to position" f" {position}"
            )
            print(f"{e}\n")
            return com.PositionalOutputData([], "Error moving " "manipulator")

    # Calibration
    def calibrate(self) -> bool:
        """Calibrate the manipulator

        :return: None
        """
        return self._x.CalibrateFrequency() and self._y.CalibrateFrequency() and self._z.CalibrateFrequency()

    def get_calibrated(self) -> bool:
        """Return the calibration state of the manipulator.

        :return: True if the manipulator is calibrated, False otherwise
        :rtype: bool
        """
        return self._calibrated

    def set_calibrated(self) -> None:
        """Set the manipulator to calibrated

        :return: None
        """
        self._calibrated = True

    def set_can_write(
            self, can_write: bool, hours: float, sio: socketio.AsyncServer
    ) -> None:
        """Set if the manipulator can move

        :param can_write: True if the manipulator can move, False otherwise
        :type can_write: bool
        :param hours: The number of hours to allow the manipulator to move (0 =
            forever)
        :type hours: float
        :param sio: SocketIO object from server to emit reset event
        :type sio: :class:`socketio.AsyncServer`
        :return: None
        """
        self._can_write = can_write

        if can_write and hours > 0:
            if self._reset_timer:
                self._reset_timer.cancel()
            self._reset_timer = threading.Timer(
                hours * 3600, self.reset_can_write, [sio]
            )
            self._reset_timer.start()

    def get_can_write(self) -> bool:
        """Return if the manipulator can move

        :return: True if the manipulator can move, False otherwise
        :rtype: bool
        """
        return self._can_write

    def reset_can_write(self, sio: socketio.AsyncServer) -> None:
        """Reset the :attr:`can_write` flag

        :param sio: SocketIO object from server to emit reset event
        :type sio: :class:`socketio.AsyncServer`
        :return: None
        """
        self._can_write = False
        asyncio.run(sio.emit("write_disabled", self._id))
