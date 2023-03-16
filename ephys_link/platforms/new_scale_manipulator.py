# noinspection PyUnresolvedReferences
from NstMotorCtrl import NstCtrlAxis
import ephys_link.common as com


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

        # Calibrate frequency
        self._x.CalibrateFrequency()
        self._y.CalibrateFrequency()
        self._z.CalibrateFrequency()

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
