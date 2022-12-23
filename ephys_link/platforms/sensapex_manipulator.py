"""Sensapex manipulator API calls

Handles logic for calling Sensapex API functions. Also includes extra logic for safe
function calls, error handling, managing per-manipulator attributes, and returning the
appropriate callback parameters like in :mod:`ephys_link.sensapex_handler`.
"""

import asyncio
import threading
from collections import deque
from copy import deepcopy

# noinspection PyPackageRequirements
import socketio
from sensapex import SensapexDevice

import ephys_link.common as com


class SensapexManipulator:
    """Representation of a single Sensapex manipulator

    :param device: A Sensapex device
    :type device: :class: `sensapex.SensapexDevice`
    """

    # How fast a manipulator is allowed to drive when inside the brain (in µm/s)
    INSIDE_BRAIN_SPEED_LIMIT = 10

    def __init__(self, device: SensapexDevice) -> None:
        """Construct a new Manipulator object"""
        self._device = device
        self._id = device.dev_id
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

    # Device functions
    def get_pos(self) -> com.PositionalOutputData:
        """Get the current position of the manipulator and convert it into mm

        :return: Callback parameters (position in (x, y, z, w) (or an empty array on
            error), error message)
        :rtype: :class:`ephys_link.common.PositionalOutputData`
        """
        try:
            position = [axis / 1000 for axis in self._device.get_pos(1)]
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
                target_position = self._device.get_pos()
                target_position[3] = position[3]
                target_speed = min(speed, self.INSIDE_BRAIN_SPEED_LIMIT)

            # Move manipulator
            movement = self._device.goto_pos(target_position, target_speed)

            # Wait for movement to finish
            while not movement.finished:
                await asyncio.sleep(0.1)

            # Get position
            manipulator_final_position = self._device.get_pos()

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

    async def drive_to_depth(
        self, depth: float, speed: int
    ) -> com.DriveToDepthOutputData:
        """Drive the manipulator to a certain depth

        :param depth: The depth to drive to
        :type depth: float
        :param speed: The speed to drive at
        :type speed: int
        :return: Callback parameters (depth (or 0 on error), error message)
        :rtype: :class:`ephys_link.common.DriveToDepthOutputData`
        """
        # Get position before this movement
        target_pos = self._device.get_pos()
        if len(self._move_queue) > 0:
            target_pos = deepcopy(self._move_queue[0].position)

        target_pos[3] = depth
        movement_result = await self.goto_pos(target_pos, speed)

        if movement_result["error"] == "":
            # Return depth on success
            return com.DriveToDepthOutputData(movement_result["position"][3], "")
        else:
            # Return 0 and error message on failure
            return com.DriveToDepthOutputData(0, "Error driving " "manipulator")

    def set_inside_brain(self, inside: bool) -> None:
        """Set if the manipulator is inside the brain

        Used to signal that the brain should move at :const:`INSIDE_BRAIN_SPEED_LIMIT`

        :param inside: True if the manipulator is inside the brain, False otherwise
        :type inside: bool
        :return: None
        """
        self._inside_brain = inside

    def get_can_write(self) -> bool:
        """Return if the manipulator can move

        :return: True if the manipulator can move, False otherwise
        :rtype: bool
        """
        return self._can_write

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

    def reset_can_write(self, sio: socketio.AsyncServer) -> None:
        """Reset the :attr:`can_write` flag

        :param sio: SocketIO object from server to emit reset event
        :type sio: :class:`socketio.AsyncServer`
        :return: None
        """
        self._can_write = False
        asyncio.run(sio.emit("write_disabled", self._id))

    # Calibration
    def call_calibrate(self) -> None:
        """Calibrate the manipulator

        :return: None
        """
        self._device.calibrate_zero_position()

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

    def stop(self) -> None:
        """Stop the manipulator

        :return: None
        """
        while self._move_queue:
            self._move_queue.pop().event.set()
        self._can_write = False
        self._device.stop()
        com.dprint(f"[SUCCESS]\t Stopped manipulator {self._id}")
