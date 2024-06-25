"""Base binding methods for Ephys Link manipulator platforms.

Definition of the methods a platform bindings class must implement to be used by Ephys Link.

Usage: Implement the BaseBindings class when defining a platform binding to ensure it supports the necessary methods.
"""

from abc import ABC, abstractmethod

from vbl_aquarium.models.unity import Vector4


class BaseBindings(ABC):
    """Base class to enforce bindings manipulator platforms will support."""

    @abstractmethod
    def get_manipulators(self) -> list[str]:
        """Get a list of available manipulators on the current platform.

        :returns: List of manipulator IDs.
        :rtype: list[str]
        """

    @abstractmethod
    def get_num_axes(self) -> int:
        """Get the number of axes for the current platform.

        :returns: Number of axes.
        :rtype: int
        """

    @abstractmethod
    def get_dimensions(self) -> Vector4:
        """Get the dimensions of the manipulators on the current platform.

        :returns: Dimensions of the manipulators.
        :rtype: Vector4
        """
