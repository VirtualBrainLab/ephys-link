"""Handle communications with platform specific API

Handles relaying WebSocket messages to the appropriate platform API functions and
conducting error checks on the input and output values

Function names here are the same as the WebSocket events. They are called when the
server receives an event from a client. In general, each function does the following:

1. Receive extracted arguments from :mod:`ephys_link.server`
2. Call and check the appropriate platform API function (overloaded by each platform)
3. Log/handle successes and failures
4. Return the callback parameters to :mod:`ephys_link.server`
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from vbl_aquarium.models.ephys_link import PositionalResponse
from vbl_aquarium.models.unity import Vector4

from ephys_link import common as com

if TYPE_CHECKING:
    import socketio


class PlatformHandler(ABC):
    """An abstract class that defines the interface for a manipulator handler."""

    def __init__(self):
        """Initialize the manipulator handler with a dictionary of manipulators."""

        # Registered manipulators are stored as a dictionary of IDs (string) to
        # manipulator objects
        self.manipulators = {}
        self.num_axes = 4

        # Platform axes dimensions in mm
        self.dimensions = Vector4(x=20, y=20, z=20, w=20)

    # Platform Handler Methods

    def reset(self) -> bool:
        """Reset handler.

        :return: True if successful, False otherwise.
        :rtype: bool
        """
        stop_result = self.stop()
        self.manipulators.clear()
        return stop_result

    def stop(self) -> bool:
        """Stop handler.

        :return: True if successful, False otherwise.
        :rtype: bool
        """
        try:
            for manipulator in self.manipulators.values():
                if hasattr(manipulator, "stop"):
                    manipulator.stop()
        except Exception as e:
            print(f"[ERROR]\t\t Could not stop manipulators: {e}\n")
            return False
        else:
            return True

    def get_manipulators(self) -> com.GetManipulatorsOutputData:
        """Get all registered manipulators.

        :return: Result of connected manipulators, platform information, and error message (if any).
        :rtype: :class:`ephys_link.common.GetManipulatorsOutputData`
        """
        error = "Error getting manipulators"
        try:
            devices = self._get_manipulators()
            error = ""
        except Exception as e:
            print(f"[ERROR]\t\t Getting manipulators: {type(e)}: {e}\n")
            return com.GetManipulatorsOutputData([], self.num_axes, self.dimensions, error)
        else:
            return com.GetManipulatorsOutputData(devices, self.num_axes, self.dimensions, error)

    def register_manipulator(self, manipulator_id: str) -> str:
        """Register a manipulator.

        :param manipulator_id: The ID of the manipulator to register.
        :type manipulator_id: str
        :return: Error message on error, empty string otherwise.
        :rtype: str
        """
        # Check if manipulator is already registered
        if manipulator_id in self.manipulators:
            print(f"[ERROR]\t\t Manipulator already registered:" f" {manipulator_id}\n")
            return "Manipulator already registered"

        try:
            # Register manipulator
            self._register_manipulator(manipulator_id)
        except ValueError as ve:
            # Manipulator not found in UMP
            print(f"[ERROR]\t\t Manipulator not found: {manipulator_id}: {ve}\n")
            return "Manipulator not found"
        except Exception as e:
            # Other error
            print(f"[ERROR]\t\t Registering manipulator: {manipulator_id}")
            print(f"{type(e)}: {e}\n")
            return "Error registering manipulator"
        else:
            com.dprint(f"[SUCCESS]\t Registered manipulator: {manipulator_id}\n")
            return ""

    def unregister_manipulator(self, manipulator_id: str) -> str:
        """Unregister a manipulator.

        :param manipulator_id: The ID of the manipulator to unregister.
        :type manipulator_id: str
        :return: Error message on error, empty string otherwise.
        :rtype: str
        """
        # Check if manipulator is not registered
        if manipulator_id not in self.manipulators:
            print(f"[ERROR]\t\t Manipulator not registered: {manipulator_id}\n")
            return "Manipulator not registered"

        try:
            # Unregister manipulator
            self._unregister_manipulator(manipulator_id)
        except Exception as e:
            # Other error
            print(f"[ERROR]\t\t Unregistering manipulator: {manipulator_id}")
            print(f"{e}\n")
            return "Error unregistering manipulator"
        else:
            com.dprint(f"[SUCCESS]\t Unregistered manipulator: {manipulator_id}\n")
            return ""

    def get_pos(self, manipulator_id: str) -> com.PositionalOutputData:
        """Get the current position of a manipulator.

        :param manipulator_id: The ID of the manipulator to get the position of.
        :type manipulator_id: str
        :return: Positional information for the manipulator and error message (if any).
        :rtype: :class:`ephys_link.common.PositionalOutputData`
        """
        try:
            # Check calibration status
            if (
                    hasattr(self.manipulators[manipulator_id], "get_calibrated")
                    and not self.manipulators[manipulator_id].get_calibrated()
            ):
                print(f"[ERROR]\t\t Calibration not complete: {manipulator_id}\n")
                return com.PositionalOutputData([], "Manipulator not calibrated")

            # Get position and convert to unified space
            manipulator_pos = self._get_pos(manipulator_id)

            # Shortcut return for Pathfinder
            if self.num_axes == -1:
                return manipulator_pos

            # Error check and convert position to unified space
            if manipulator_pos["error"] != "":
                return manipulator_pos
            return com.PositionalOutputData(self._platform_space_to_unified_space(manipulator_pos["position"]), "")
        except KeyError:
            # Manipulator not found in registered manipulators
            print(f"[ERROR]\t\t Manipulator not registered: {manipulator_id}")
            return com.PositionalOutputData([], "Manipulator not registered")

    def get_angles(self, manipulator_id: str) -> com.AngularOutputData:
        """Get the current position of a manipulator.

        :param manipulator_id: The ID of the manipulator to get the angles of.
        :type manipulator_id: str
        :return: Angular information for the manipulator and error message (if any).
        :rtype: :class:`ephys_link.common.AngularOutputData`
        """
        try:
            # Check calibration status
            if (
                    hasattr(self.manipulators[manipulator_id], "get_calibrated")
                    and not self.manipulators[manipulator_id].get_calibrated()
            ):
                print(f"[ERROR]\t\t Calibration not complete: {manipulator_id}\n")
                return com.AngularOutputData([], "Manipulator not calibrated")

            # Get position
            return self._get_angles(manipulator_id)

        except KeyError:
            # Manipulator not found in registered manipulators
            print(f"[ERROR]\t\t Manipulator not registered: {manipulator_id}")
            return com.AngularOutputData([], "Manipulator not registered")

    def get_shank_count(self, manipulator_id: str) -> com.ShankCountOutputData:
        """Get the number of shanks on the probe

        :param manipulator_id: The ID of the manipulator to get the number of shanks of.
        :type manipulator_id: str
        :return: Number of shanks on the probe.
        :rtype: :class:`ephys_link.common.ShankCountOutputData`
        """
        return self._get_shank_count(manipulator_id)

    async def goto_pos(self, manipulator_id: str, position: Vector4, speed: float) -> PositionalResponse:
        """Move manipulator to position

        :param manipulator_id: The ID of the manipulator to move
        :type manipulator_id: str
        :param position: The position to move to in (x, y, z, w) in mm
        :type position: Vector4
        :param speed: The speed to move at (in mm/s)
        :type speed: float
        :return: Resulting position of the manipulator and error message (if any).
        :rtype: :class:`vbl_aquarium.models.ephys_link.PositionalResponse`
        """
        try:
            # Check calibration status
            if not self.manipulators[manipulator_id].get_calibrated():
                print(f"[ERROR]\t\t Calibration not complete: {manipulator_id}\n")
                return PositionalResponse(error="Manipulator not calibrated")

            # Check write state
            if not self.manipulators[manipulator_id].get_can_write():
                print(f"[ERROR]\t\t Cannot write to manipulator: {manipulator_id}")
                return PositionalResponse(error="Cannot write to manipulator")

            # Convert position to platform space, move, and convert final position back to
            # unified space
            end_position = await self._goto_pos(manipulator_id, self._unified_space_to_platform_space(position), speed)
            if end_position.error != "":
                return end_position
            return PositionalResponse(position=self._platform_space_to_unified_space(end_position.position))

        except KeyError:
            # Manipulator not found in registered manipulators
            print(f"[ERROR]\t\t Manipulator not registered: {manipulator_id}\n")
            return PositionalResponse(error="Manipulator not registered")

    async def drive_to_depth(self, manipulator_id: str, depth: float, speed: float) -> com.DriveToDepthOutputData:
        """Drive manipulator to depth

        :param manipulator_id: The ID of the manipulator to drive
        :type manipulator_id: str
        :param depth: The depth to drive to in mm
        :type depth: float
        :param speed: The speed to drive at (in mm/s)
        :type speed: float
        :return: Resulting depth of the manipulator and error message (if any).
        :rtype: :class:`ephys_link.common.DriveToDepthOutputData`
        """
        try:
            # Check calibration status
            if not self.manipulators[manipulator_id].get_calibrated():
                print(f"[ERROR]\t\t Calibration not complete: {manipulator_id}\n")
                return com.DriveToDepthOutputData(0, "Manipulator not calibrated")

            # Check write state
            if not self.manipulators[manipulator_id].get_can_write():
                print(f"[ERROR]\t\t Cannot write to manipulator: {manipulator_id}")
                return com.DriveToDepthOutputData(0, "Cannot write to manipulator")

            end_depth = await self._drive_to_depth(
                manipulator_id,
                self._unified_space_to_platform_space([0, 0, 0, depth])[3],
                speed,
            )
            if end_depth["error"] != "":
                return end_depth
            return com.DriveToDepthOutputData(
                self._platform_space_to_unified_space([0, 0, 0, end_depth["depth"]])[3],
                "",
            )

        except KeyError:
            # Manipulator not found in registered manipulators
            print(f"[ERROR]\t\t Manipulator not registered: {manipulator_id}\n")
            return com.DriveToDepthOutputData(0, "Manipulator " "not registered")

    def set_inside_brain(self, manipulator_id: str, inside: bool) -> com.StateOutputData:
        """Set manipulator inside brain state (restricts motion)

        :param manipulator_id: The ID of the manipulator to set the state of
        :type manipulator_id: str
        :param inside: True if inside brain, False if outside
        :type inside: bool
        :return: New inside brain state of the manipulator and error message (if any).
        :rtype: :class:`ephys_link.common.StateOutputData`
        """
        try:
            # Check calibration status
            if (
                    hasattr(self.manipulators[manipulator_id], "get_calibrated")
                    and not self.manipulators[manipulator_id].get_calibrated()
            ):
                print("[ERROR]\t\t Calibration not complete\n")
                return com.StateOutputData(False, "Manipulator not calibrated")

            return self._set_inside_brain(manipulator_id, inside)

        except KeyError:
            # Manipulator not found in registered manipulators
            print(f"[ERROR]\t\t Manipulator {manipulator_id} not registered\n")
            return com.StateOutputData(False, "Manipulator not " "registered")

        except Exception as e:
            # Other error
            print(f"[ERROR]\t\t Set manipulator {manipulator_id} inside brain " f"state")
            print(f"{e}\n")
            return com.StateOutputData(False, "Error setting " "inside brain")

    async def calibrate(self, manipulator_id: str, sio: socketio.AsyncServer) -> str:
        """Calibrate manipulator

        :param manipulator_id: ID of manipulator to calibrate
        :type manipulator_id: str
        :param sio: SocketIO object (to call sleep)
        :type sio: :class:`socketio.AsyncServer`
        :return: Error message on error, empty string otherwise.
        :rtype: str
        """
        try:
            # Check write state
            if not self.manipulators[manipulator_id].get_can_write():
                print(f"[ERROR]\t\t Cannot write to manipulator: {manipulator_id}")
                return "Cannot write to manipulator"

            return await self._calibrate(manipulator_id, sio)

        except KeyError:
            # Manipulator not found in registered manipulators
            print(f"[ERROR]\t\t Manipulator {manipulator_id} not registered\n")
            return "Manipulator not registered"

        except Exception as e:
            # Other error
            print(f"[ERROR]\t\t Calibrate manipulator {manipulator_id}")
            print(f"{e}\n")
            return "Error calibrating manipulator"

    def bypass_calibration(self, manipulator_id: str) -> str:
        """Bypass calibration of manipulator

        :param manipulator_id: ID of manipulator to bypass calibration
        :type manipulator_id: str
        :return: Error message on error, empty string otherwise.
        :rtype: str
        """
        try:
            # Bypass calibration
            return self._bypass_calibration(manipulator_id)

        except KeyError:
            # Manipulator not found in registered manipulators
            print(f"[ERROR]\t\t Manipulator {manipulator_id} not registered\n")
            return "Manipulator not registered"

        except Exception as e:
            # Other error
            print(f"[ERROR]\t\t Bypass calibration of manipulator {manipulator_id}")
            print(f"{e}\n")
            return "Error bypassing calibration"

    def set_can_write(
            self,
            manipulator_id: str,
            can_write: bool,
            hours: float,
            sio: socketio.AsyncServer,
    ) -> com.StateOutputData:
        """Set manipulator can_write state (enables/disabled moving manipulator)

        :param manipulator_id: The ID of the manipulator to set the state of
        :type manipulator_id: str
        :param can_write: True if allowed to move, False if outside
        :type can_write: bool
        :param hours: The number of hours to allow writing (0 = forever)
        :type hours: float
        :param sio: SocketIO object from server to emit reset event
        :type sio: :class:`socketio.AsyncServer`
        :return: New can_write state of the manipulator and error message (if any).
        :rtype: :class:`ephys_link.common.StateOutputData`
        """
        try:
            return self._set_can_write(manipulator_id, can_write, hours, sio)
        except KeyError:
            # Manipulator not found in registered manipulators
            print(f"[ERROR]\t\t Manipulator not registered: {manipulator_id}\n")
            return com.StateOutputData(False, "Manipulator not " "registered")
        except Exception as e:
            # Other error
            print(f"[ERROR]\t\t Set manipulator {manipulator_id} can_write state")
            print(f"{e}\n")
            return com.StateOutputData(False, "Error setting " "can_write")

    # Platform specific methods to override

    @abstractmethod
    def _get_manipulators(self) -> list:
        raise NotImplementedError

    @abstractmethod
    def _register_manipulator(self, manipulator_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def _unregister_manipulator(self, manipulator_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def _get_pos(self, manipulator_id: str) -> com.PositionalOutputData:
        raise NotImplementedError

    @abstractmethod
    def _get_angles(self, manipulator_id: str) -> com.AngularOutputData:
        raise NotImplementedError

    @abstractmethod
    def _get_shank_count(self, manipulator_id: str) -> com.ShankCountOutputData:
        raise NotImplementedError

    @abstractmethod
    async def _goto_pos(self, manipulator_id: str, position: Vector4, speed: float) -> PositionalResponse:
        raise NotImplementedError

    @abstractmethod
    async def _drive_to_depth(self, manipulator_id: str, depth: float, speed: float) -> com.DriveToDepthOutputData:
        raise NotImplementedError

    @abstractmethod
    def _set_inside_brain(self, manipulator_id: str, inside: bool) -> com.StateOutputData:
        raise NotImplementedError

    @abstractmethod
    async def _calibrate(self, manipulator_id: str, sio: socketio.AsyncServer) -> str:
        """Calibrate manipulator

        :param manipulator_id: ID of manipulator to calibrate
        :type manipulator_id: str
        :param sio: SocketIO object (to call sleep)
        :type sio: :class:`socketio.AsyncServer`
        :return: Callback parameters (manipulator ID, error message)
        :rtype: str
        """

    @abstractmethod
    def _bypass_calibration(self, manipulator_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def _set_can_write(
            self,
            manipulator_id: str,
            can_write: bool,
            hours: float,
            sio: socketio.AsyncServer,
    ) -> com.StateOutputData:
        raise NotImplementedError

    @abstractmethod
    def _platform_space_to_unified_space(self, platform_position: Vector4) -> Vector4:
        """Convert position in platform space to position in unified manipulator space

        :param platform_position: Position in platform space (x, y, z, w) in mm
        :type platform_position: Vector4
        :return: Position in unified manipulator space (x, y, z, w) in mm
        :rtype: Vector4
        """
        raise NotImplementedError

    @abstractmethod
    def _unified_space_to_platform_space(self, unified_position: Vector4) -> Vector4:
        """Convert position in unified manipulator space to position in platform space

        :param unified_position: Position in unified manipulator space (x, y, z, w) in mm
        :type unified_position: Vector4
        :return: Position in platform space (x, y, z, w) in mm
        :rtype: Vector4
        """
        raise NotImplementedError
