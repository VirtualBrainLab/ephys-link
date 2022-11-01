from abc import ABC, abstractmethod
import common as com

# noinspection PyPackageRequirements
import socketio


class PlatformHandler(ABC):
    """An abstract class that defines the interface for a manipulator handler."""

    def __init__(self):
        """Initialize the manipulator handler with a dictionary of manipulators."""
        self.manipulators = {}

    def reset(self) -> bool:
        """Reset handler

        :return: True if successful, False otherwise
        :rtype: bool
        """
        stop_result = self.stop()
        self.manipulators.clear()
        return stop_result

    def stop(self) -> bool:
        """Stop handler

            :return: True if successful, False otherwise
            :rtype: bool
            """
        try:
            for manipulator in self.manipulators.values():
                manipulator.stop()
            return True
        except Exception as e:
            print(f"[ERROR]\t\t Stopping manipulators: {e}\n")
            return False

    @abstractmethod
    def get_manipulators(self) -> com.GetManipulatorsOutputData:
        """Get all registered manipulators

        :return: Callback parameters (manipulators, error)
        :rtype: :class:`ephys_link.common.GetManipulatorsOutputData`
        """
        pass

    @abstractmethod
    def register_manipulator(self, manipulator_id: int) -> str:
        """Register a manipulator

        :param manipulator_id: The ID of the manipulator to register.
        :type manipulator_id: int
        :return: Callback parameter (Error message (on error))
        :rtype: str
        """
        pass

    @abstractmethod
    def unregister_manipulator(self, manipulator_id: int) -> str:
        """Unregister a manipulator

        :param manipulator_id: The ID of the manipulator to unregister.
        :type manipulator_id: int
        :return: Callback parameters (error message (on error))
        """
        pass

    @abstractmethod
    def get_pos(self, manipulator_id: int) -> com.PositionalOutputData:
        """Get the current position of a manipulator

        :param manipulator_id: The ID of the manipulator to get the position of.
        :type manipulator_id: int
        :return: Callback parameters (manipulator ID, position in (x, y, z, w) (or an
            empty array on error), error message)
        :rtype: :class:`ephys_link.common.PositionalOutputData`
        """
        pass

    @abstractmethod
    async def goto_pos(self,
                       manipulator_id: int, position: list[float], speed: int
                       ) -> com.PositionalOutputData:
        """Move manipulator to position

        :param manipulator_id: The ID of the manipulator to move
        :type manipulator_id: int
        :param position: The position to move to
        :type position: list[float]
        :param speed: The speed to move at (in µm/s)
        :type speed: int
        :return: Callback parameters (manipulator ID, position in (x, y, z, w) (or an
                 empty array on error), error message)
        :rtype: :class:`ephys_link.common.PositionalOutputData`
        """
        pass

    @abstractmethod
    async def drive_to_depth(self,
                             manipulator_id: int, depth: float, speed: int
                             ) -> com.DriveToDepthOutputData:
        """Drive manipulator to depth

        :param manipulator_id: The ID of the manipulator to drive
        :type manipulator_id: int
        :param depth: The depth to drive to
        :type depth: float
        :param speed: The speed to drive at (in µm/s)
        :type speed: int
        :return: Callback parameters (manipulator ID, depth (or 0 on error), error
                 message)
        :rtype: :class:`ephys_link.common.DriveToDepthOutputData`
        """
        pass

    @abstractmethod
    def set_inside_brain(self, manipulator_id: int,
                         inside: bool) -> com.StateOutputData:
        """Set manipulator inside brain state (restricts motion)

        :param manipulator_id: The ID of the manipulator to set the state of
        :type manipulator_id: int
        :param inside: True if inside brain, False if outside
        :type inside: bool
        :return: Callback parameters (manipulator ID, inside, error message)
        :rtype: :class:`ephys_link.common.StateOutputData`
        """
        pass

    @abstractmethod
    async def calibrate(self, manipulator_id: int, sio: socketio.AsyncServer) -> str:
        """Calibrate manipulator

        :param manipulator_id: ID of manipulator to calibrate
        :type manipulator_id: int
        :param sio: SocketIO object (to call sleep)
        :type sio: :class:`socketio.AsyncServer`
        :return: Callback parameters (manipulator ID, error message)
        :rtype: str
        """

    @abstractmethod
    def bypass_calibration(self, manipulator_id: int) -> str:
        """Bypass calibration of manipulator

        :param manipulator_id: ID of manipulator to bypass calibration
        :type manipulator_id: int
        :return: Callback parameters (manipulator ID, error message)
        :rtype: str
        """
        pass

    @abstractmethod
    def set_can_write(self,
                      manipulator_id: int, can_write: bool, hours: float,
                      sio: socketio.AsyncServer
                      ) -> com.StateOutputData:
        """Set manipulator can_write state (enables/disabled moving manipulator)

        :param manipulator_id: The ID of the manipulator to set the state of
        :type manipulator_id: int
        :param can_write: True if allowed to move, False if outside
        :type can_write: bool
        :param hours: The number of hours to allow writing (0 = forever)
        :type hours: float
        :param sio: SocketIO object from server to emit reset event
        :type sio: :class:`socketio.AsyncServer`
        :return: Callback parameters (manipulator ID, can_write, error message)
        :rtype: :class:`ephys_link.common.StateOutputData`
        """
        pass
