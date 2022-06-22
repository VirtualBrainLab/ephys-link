from typing import List

from sensapex import SensapexDevice


class Manipulator:
    def __init__(self, device: SensapexDevice):
        """
        Construct a new Manipulator object
        :param device: A Sensapex device
        """
        self._device = device
        self._id = device.dev_id
        self._calibrated = False

    # Device functions
    def get_pos(self):
        """
        Get the current position of the manipulator
        :return: Callback parameters [Manipulator ID, position in [x, y, z,
        w] (or an empty array on error), error message]
        """
        try:
            position = self._device.get_pos()
            print(f'[SUCCESS]\t Sent position of manipulator {self._id}\n')
            return self._id, position, ''
        except Exception as e:
            print(f'[ERROR]\t\t Getting position of manipulator {self._id}')
            print(f'{e}\n')
            return self._id, [], 'Error getting position'

    def goto_pos(self, position: List[float], speed: float) \
            -> (int, List[float], str):
        """
        Move manipulator to position
        :param position: The position to move to
        :param speed: The speed to move at (in um/s)
        :return: Callback parameters [Manipulator ID, position in [x, y, z,
        w] (or an empty array on error), error message]
        """
        try:
            # Move manipulator
            movement = self._device.goto_pos(
                position,
                speed)

            # Wait for movement to finish
            movement.finished_event.wait()

            # Get position
            manipulator_final_position = self._device.get_pos()

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
            return self._id, [], 'Error moving manipulator'

    # Calibration status
    def get_calibrated(self) -> bool:
        """
        Return the calibration state of the manipulator.
        :return: True if the manipulator is calibrated, False otherwise
        """
        return self._calibrated

    def set_calibrated(self):
        """Set the manipulator to calibrated"""
        self._calibrated = True
