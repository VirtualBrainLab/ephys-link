from sensapex import SensapexDevice


class Manipulator:
    def __init__(self, device: SensapexDevice):
        """
        Construct a new Manipulator object
        :param device: A Sensapex device
        """
        self.device = device
        self.calibrated = False

    def get_calibrated(self):
        """Return the calibration state of the manipulator."""
        return self.calibrated

    def set_calibrated(self):
        """Set the manipulator to calibrated"""
        self.calibrated = True
