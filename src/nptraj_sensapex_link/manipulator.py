import asyncio
from collections import deque
from sensapex import SensapexDevice


class Manipulator:
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
        self._move_queue = deque()

    # Device functions
    def get_pos(self) -> (int, tuple[float], str):
        """
        Get the current position of the manipulator
        :return: Callback parameters (manipulator ID, position in (x, y, z,
        w) (or an empty array on error), error message)
        """
        try:
            position = tuple(self._device.get_pos())
            print(f'[SUCCESS]\t Sent position of manipulator {self._id}\n')
            return self._id, position, ''
        except Exception as e:
            print(f'[ERROR]\t\t Getting position of manipulator {self._id}')
            print(f'{e}\n')
            return self._id, [], 'Error getting position'

    async def goto_pos(self, position: list[float], speed: float) \
            -> (int, tuple[float], str):
        """
        Move manipulator to position
        :param position: The position to move to
        :param speed: The speed to move at (in um/s)
        :return: Callback parameters (manipulator ID, position in (x, y, z,
        w) (or an empty array on error), error message)
        """
        # Add movement flag to queue
        self._move_queue.appendleft(asyncio.Event())

        # Wait for preceding movement to finish
        if len(self._move_queue) > 1:
            await self._move_queue[1].wait()

        try:
            target_position = position

            # Alter target position if inside brain
            if self._inside_brain:
                target_position = self._device.get_pos()
                target_position[3] = position[3]

            # Move manipulator
            movement = self._device.goto_pos(target_position, speed)

            # Wait for movement to finish
            while not movement.finished:
                await asyncio.sleep(0.1)

            # Get position
            manipulator_final_position = tuple(self._device.get_pos())

            # Remove event from queue and mark as completed
            self._move_queue.pop().set()

            print(
                f'[SUCCESS]\t Moved manipulator {self._id} to position'
                f' {manipulator_final_position}\n'
            )
            return self._id, manipulator_final_position, ''
        except Exception as e:
            print(
                f'[ERROR]\t\t Moving manipulator {self._id} to position'
                f' {position}')
            print(f'{e}\n')
            return self._id, (), 'Error moving manipulator'

    async def drive_to_depth(self, depth: float, speed: int) -> (int, float,
                                                                 str):
        """
        Drive the manipulator to a certain depth
        :param depth: The depth to drive to
        :param speed: The speed to drive at
        :return: Callback parameters (manipulator ID, depth (or 0 on error),
        error message)
        """
        target_pos = self._device.get_pos()
        target_pos[3] = depth
        movement_result = await self.goto_pos(target_pos, speed)

        if movement_result[2] == '':
            # Return depth on success
            return self._id, movement_result[1][3], ''
        else:
            # Return 0 and error message on failure
            return self._id, 0, movement_result[2]

    def set_inside_brain(self, inside: bool) -> None:
        """
        Set if the manipulator is inside the brain (and movement should
        be restricted)
        :param inside: True if the manipulator is inside the brain,
        False otherwise
        :return: None
        """
        self._inside_brain = inside

    # Calibration
    def call_calibrate(self) -> None:
        """Calibrate the manipulator"""
        self._device.calibrate_zero_position()

    def get_calibrated(self) -> bool:
        """
        Return the calibration state of the manipulator.
        :return: True if the manipulator is calibrated, False otherwise
        """
        return self._calibrated

    def set_calibrated(self) -> None:
        """Set the manipulator to calibrated"""
        self._calibrated = True
