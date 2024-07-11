"""Binding methods for Ephys Link manipulator platforms.

Definition of the methods a platform binding class must implement to be used by Ephys Link.

Usage: Implement the BaseBindings class when defining a platform binding to ensure it supports the necessary methods.
"""

from abc import ABC, abstractmethod

from vbl_aquarium.models.unity import Vector3, Vector4


class BaseBindings(ABC):
    """Base class to enforce bindings manipulator platforms will support.

    No need to catch exceptions as the Platform Handler will catch them.
    """

    @abstractmethod
    async def get_manipulators(self) -> list[str]:
        """Get a list of available manipulators on the current platform.

        :returns: List of manipulator IDs.
        :rtype: list[str]
        """

    @abstractmethod
    async def get_num_axes(self) -> int:
        """Get the number of axes for the current platform.

        :returns: Number of axes.
        :rtype: int
        """

    @abstractmethod
    def get_dimensions(self) -> Vector4:
        """Get the dimensions of the manipulators on the current platform (mm).

        For 3-axis manipulators, copy the dimension of the axis parallel to the probe into w.

        :returns: Dimensions of the manipulators.
        :rtype: Vector4
        """

    @abstractmethod
    async def get_position(self, manipulator_id: str) -> Vector4:
        """Get the current position of a manipulator.

        These will be the translation values of the manipulator (mm), so they may need to be rotated to unified space.
        For 3-axis manipulators, copy the position of the axis parallel to the probe into w.

        :param manipulator_id: Manipulator ID.
        :type manipulator_id: str
        :returns: Current position of the manipulator in platform space (mm).
        :rtype: Vector4
        """

    @abstractmethod
    async def get_angles(self, manipulator_id: str) -> Vector3:
        """Get the current rotation angles of a manipulator in Yaw, Pitch, Roll (degrees).

        :param manipulator_id: Manipulator ID.
        :type manipulator_id: str
        :returns: Current angles of the manipulator.
        :rtype: Vector3
        """

    @abstractmethod
    async def get_shank_count(self, manipulator_id: str) -> int:
        """Get the number of shanks on a manipulator.

        :param manipulator_id: Manipulator ID.
        :type manipulator_id: str
        :returns: Number of shanks on the manipulator.
        :rtype: int
        """

    @abstractmethod
    def get_movement_tolerance(self) -> float:
        """Get the tolerance for how close the final position must be to the target position in a movement (mm).

        :returns: Movement tolerance (mm).
        :rtype: float
        """

    @abstractmethod
    async def set_position(self, manipulator_id: str, position: Vector4, speed: float) -> Vector4:
        """Set the position of a manipulator.

        This will directly set the position in the original platform space.
        Unified space coordinates will need to be converted to platform space.
        For 3-axis manipulators, the first 3 values of the position will be used.

        :param manipulator_id: Manipulator ID.
        :type manipulator_id: str
        :param position: Platform space position to set the manipulator to (mm).
        :type position: Vector4
        :param speed: Speed to move the manipulator to the position (mm/s).
        :type speed: float
        :returns: Final position of the manipulator in platform space (mm).
        :rtype: Vector4
        """

    @abstractmethod
    async def stop(self, manipulator_id: str) -> None:
        """Stop a manipulator."""

    @abstractmethod
    def platform_space_to_unified_space(self, platform_space: Vector4) -> Vector4:
        """Convert platform space coordinates to unified space coordinates.

        This is an axes-swapping transformation.

        Unified coordinate space is the standard left-handed cartesian coordinate system
        with an additional depth axis pointing from the base of the probe to the tip.

        :param platform_space: Platform space coordinates.
        :type platform_space: Vector4
        :returns: Unified space coordinates.
        :rtype: Vector4
        """

    @abstractmethod
    def unified_space_to_platform_space(self, unified_space: Vector4) -> Vector4:
        """Convert unified space coordinates to platform space coordinates.

        This is an axes-swapping transformation.

        :param unified_space: Unified space coordinates.
        :type unified_space: Vector4
        :returns: Platform space coordinates.
        :rtype: Vector4
        """
