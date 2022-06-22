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

    def get_device(self):
        """Temp function"""
        return self._device

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
