"""Binding methods for Ephys Link manipulator platforms.

Definition of the methods a platform binding class must implement to be used by Ephys Link.

Usage:
    Implement the BaseBindings class when defining a platform binding to ensure it supports the necessary methods.
"""

from abc import ABC, abstractmethod

from vbl_aquarium.models.unity import Vector3, Vector4


class BaseBinding(ABC):
    """Base class to enforce bindings manipulator platforms will support.

    No need to catch exceptions as the [Platform Handler][ephys_link.back_end.platform_handler] will catch them.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the platform binding with any necessary arguments."""

    @staticmethod
    @abstractmethod
    def get_display_name() -> str:
        """Get the full display name of the platform.

        Returns:
            Full display name of the platform.
        """

    @staticmethod
    @abstractmethod
    def get_cli_name() -> str:
        """Get the name of the platform for CLI usage.

        This is the value used to identify the platform when using the `-t` flag in the CLI.

        Returns:
            Name of the platform to use on the CLI.
        """

    @abstractmethod
    async def get_axes_count(self) -> int:
        """Get the number of axes for the current platform.

        Returns:
            Number of axes.
        """

    @abstractmethod
    async def get_dimensions(self) -> Vector4:
        """Get the dimensions of the manipulators on the current platform (mm).

        For 3-axis manipulators, copy the dimension of the axis parallel to the probe into w.

        Returns:
            Dimensions of the manipulators.
        """

    @abstractmethod
    async def get_manipulators(self) -> list[str]:
        """Get a list of available manipulators on the current platform.

        Returns:
            List of manipulator IDs.
        """

    @abstractmethod
    async def get_position(self, manipulator_id: str) -> Vector4:
        """Get the current position of a manipulator.

        These will be the translation values of the manipulator (mm), so they may need to be rotated to unified space.
        For 3-axis manipulators, copy the position of the axis parallel to the probe into w.

        Args:
            manipulator_id: Manipulator ID.

        Returns:
            Current position of the manipulator in platform space (mm).
        """

    @abstractmethod
    async def get_angles(self, manipulator_id: str) -> Vector3:
        """Get the current rotation angles of a manipulator in Yaw, Pitch, Roll (degrees).

        Args:
            manipulator_id: Manipulator ID.

        Returns:
            Current angles of the manipulator.
        """

    @abstractmethod
    async def get_shank_count(self, manipulator_id: str) -> int:
        """Get the number of shanks on a manipulator.

        Args:
            manipulator_id: Manipulator ID.

        Returns:
            Number of shanks on the manipulator.
        """

    @abstractmethod
    def get_movement_tolerance(self) -> float:
        """Get the tolerance for how close the final position must be to the target position in a movement (mm).

        Returns:
            Movement tolerance (mm).
        """

    @abstractmethod
    async def set_position(self, manipulator_id: str, position: Vector4, speed: float) -> Vector4:
        """Set the position of a manipulator.

        This will directly set the position in the original platform space.
        For 3-axis manipulators, the first 3 values of the position will be used.

        Args:
            manipulator_id: Manipulator ID.
            position: Platform space position to set the manipulator to (mm).
            speed: Speed to move the manipulator to the position (mm/s).

        Returns:
            Final position of the manipulator in platform space (mm).
        """

    @abstractmethod
    async def set_depth(self, manipulator_id: str, depth: float, speed: float) -> float:
        """Set the depth of a manipulator.

        This will directly set the depth stage in the original platform space.

        Args:
            manipulator_id: Manipulator ID.
            depth: Depth to set the manipulator to (mm).
            speed: Speed to move the manipulator to the depth (mm/s).

        Returns:
            Final depth of the manipulator in platform space (mm).
        """

    @abstractmethod
    async def stop(self, manipulator_id: str) -> None:
        """Stop a manipulator.

        Args:
            manipulator_id: Manipulator ID.
        """

    @abstractmethod
    def platform_space_to_unified_space(self, platform_space: Vector4) -> Vector4:
        """Convert platform space coordinates to unified space coordinates.

        This is an axes-swapping transformation.

        Unified coordinate space is the standard left-handed cartesian coordinate system
        with an additional depth axis pointing from the base of the probe to the tip.

        Args:
            platform_space: Platform space coordinates.

        Returns:
            Unified space coordinates.
        """

    @abstractmethod
    def unified_space_to_platform_space(self, unified_space: Vector4) -> Vector4:
        """Convert unified space coordinates to platform space coordinates.

        This is an axes-swapping transformation.

        Args:
            unified_space: Unified space coordinates.

        Returns:
            Platform space coordinates.
        """
