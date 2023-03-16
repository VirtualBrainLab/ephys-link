# noinspection PyUnresolvedReferences
from NstMotorCtrl import NstCtrlAxis


class NewScaleManipulator:
    def __init__(self, manipulator_id: str, x_axis: NstCtrlAxis, y_axis: NstCtrlAxis, z_axis: NstCtrlAxis) -> None:
        """Construct a new Manipulator object

        :param manipulator_id: Manipulator ID
        :param x_axis: X axis object
        :param y_axis: Y axis object
        :param z_axis: Z axis object
        """

        self.id = manipulator_id
        self.x = x_axis
        self.y = y_axis
        self.z = z_axis

        # Calibrate frequency
        self.x.CalibrateFrequency()
        self.y.CalibrateFrequency()
        self.z.CalibrateFrequency()
