import asyncio
import common as com
import threading
from collections import deque
from copy import deepcopy
from sensapex import SensapexDevice


class Manipulator:
    """Representation of a single manipulator"""
    INSIDE_BRAIN_SPEED_LIMIT = 10

    def __init__(self, device: SensapexDevice) -> None:
        """
        Construct a new Manipulator object
        :param device: A Sensapex device
        :return: None
        """
        self._device = device
        self._id = device.dev_id
        self._calibrated = False
        self._inside_brain = False
        self._can_write = False
        self._reset_timer = None
        self._move_queue = deque()

    class Movement:
        """Movement struct"""

        def __init__(self, event: asyncio.Event, position: list[float]):
            """
            Construct a new Movement object
            :param event: An asyncio event
            :param position: A tuple of floats (x, y, z, w) representing the
            position to move to in µm
            """
            self.event = event
            self.position = position

    # Device functions
    def get_pos(self) -> com.PositionalOutputData:
        """
        Get the current position of the manipulator
        :return: Callback parameters (manipulator ID, position in (x, y, z,
        w) (or an empty array on error), error message)
        """
        try:
            position = tuple(self._device.get_pos(1))
            com.dprint(
                f'[SUCCESS]\t Sent position of manipulator {self._id}\n')
            return com.PositionalOutputData(self._id, position, '')
        except Exception as e:
            print(f'[ERROR]\t\t Getting position of manipulator {self._id}')
            print(f'{e}\n')
            return com.PositionalOutputData(self._id, (),
                                            'Error getting position')

    async def goto_pos(self, position: list[float], speed: float) \
            -> com.PositionalOutputData:
        """
        Move manipulator to position
        :param position: The position to move to
        :param speed: The speed to move at (in µm/s)
        :return: Callback parameters (manipulator ID, position in (x, y, z,
        w) (or an empty array on error), error message)
        """
        # Add movement to queue
        self._move_queue.appendleft(self.Movement(asyncio.Event(), position))

        # Wait for preceding movement to finish
        if len(self._move_queue) > 1:
            await self._move_queue[1].event.wait()

        if not self._can_write:
            print(f'[ERROR]\t\t Manipulator {self._id} movement '
                  f'canceled')
            return com.PositionalOutputData(self._id, (), 'Manipulator '
                                                          'movement canceled')

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
            manipulator_final_position = tuple(self._device.get_pos())

            # Remove event from queue and mark as completed
            self._move_queue.pop().event.set()

            com.dprint(
                f'[SUCCESS]\t Moved manipulator {self._id} to position'
                f' {manipulator_final_position}\n'
            )
            return com.PositionalOutputData(self._id,
                                            manipulator_final_position, '')
        except Exception as e:
            print(
                f'[ERROR]\t\t Moving manipulator {self._id} to position'
                f' {position}')
            print(f'{e}\n')
            return com.PositionalOutputData(self._id, (), 'Error moving '
                                                          'manipulator')

    async def drive_to_depth(self, depth: float, speed: int) -> (int, float,
                                                                 str):
        """
        Drive the manipulator to a certain depth
        :param depth: The depth to drive to
        :param speed: The speed to drive at
        :return: Callback parameters (manipulator ID, depth (or 0 on error),
        error message)
        """
        # Get position before this movement
        target_pos = self._device.get_pos()
        if len(self._move_queue) > 0:
            target_pos = deepcopy(self._move_queue[0].position)

        target_pos[3] = depth
        movement_result = await self.goto_pos(target_pos, speed)

        if movement_result[2] == '':
            # Return depth on success
            return self._id, movement_result[1][3], ''
        else:
            # Return 0 and error message on failure
            return self._id, 0, 'Error driving manipulator'

    def set_inside_brain(self, inside: bool) -> None:
        """
        Set if the manipulator is inside the brain (and movement should
        be restricted)
        :param inside: True if the manipulator is inside the brain,
        False otherwise
        :return: None
        """
        self._inside_brain = inside

    def get_can_write(self) -> bool:
        """
        Return if the manipulator can move
        :return: True if the manipulator can move, False otherwise
        """
        return self._can_write

    def set_can_write(self, can_write: bool, hours: float, sio) -> None:
        """
        Set if the manipulator can move
        :param can_write: True if the manipulator can move, False otherwise
        :param hours: The number of hours to allow the manipulator to move (
        0 = forever)
        :param sio: SocketIO object from server to emit reset event
        :return: None
        """
        self._can_write = can_write

        if can_write and hours > 0:
            if self._reset_timer:
                self._reset_timer.cancel()
            self._reset_timer = threading.Timer(hours * 3600,
                                                self.reset_can_write, [sio])
            self._reset_timer.start()

    def reset_can_write(self, sio):
        """Reset the can_write flag"""
        self._can_write = False
        asyncio.run(sio.emit('write_disabled', self._id))

    # Calibration
    def call_calibrate(self):
        """Calibrate the manipulator"""
        self._device.calibrate_zero_position()

    def get_calibrated(self) -> bool:
        """
        Return the calibration state of the manipulator.
        :return: True if the manipulator is calibrated, False otherwise
        """
        return self._calibrated

    def set_calibrated(self):
        """Set the manipulator to calibrated"""
        self._calibrated = True

    def stop(self):
        """Stop the manipulator"""
        while self._move_queue:
            self._move_queue.pop().event.set()
        self._can_write = False
        self._device.stop()
        com.dprint(f"[SUCCESS]\t Stopped manipulator {self._id}")
