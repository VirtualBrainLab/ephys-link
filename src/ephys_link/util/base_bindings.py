"""Base binding methods for Ephys Link manipulator platforms.

Definition of the methods a platform bindings class must implement to be used by Ephys Link.

Usage: Implement the BaseBindings class when defining a platform binding to ensure it supports the necessary methods.
"""

from abc import ABC, abstractmethod

from vbl_aquarium.models.unity import Vector4


class BaseBindings(ABC):
    """Base class to enforce bindings manipulator platforms will support."""

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
    async def get_dimensions(self) -> Vector4:
        """Get the dimensions of the manipulators on the current platform.
        
        For 3-axis manipulators, copy the dimension of the axis parallel to the probe into w.

        :returns: Dimensions of the manipulators.
        :rtype: Vector4
        """

    @abstractmethod
    async def get_pos(self, manipulator_id: str) -> Vector4:
        """Get the current position of a manipulator.

        These will be the raw values from the manipulator, so they may need to be converted to unified space.
        For 3-axis manipulators, copy the position of the axis parallel to the probe into w.
        
        :param manipulator_id: Manipulator ID.
        :type manipulator_id: str
        :returns: Current position of the manipulator.
        :rtype: Vector4
        """
    
    @abstractmethod
    async def platform_space_to_unified_space(self, platform_space: Vector4) -> Vector4:
        """Convert platform space coordinates to unified space coordinates.
        
        This is an axes-swapping transformation.

        :param platform_space: Platform space coordinates.
        :type platform_space: Vector4
        :returns: Unified space coordinates.
        :rtype: Vector4
        """
    
    @abstractmethod
    async def unified_space_to_platform_space(self, unified_space: Vector4) -> Vector4:
        """Convert unified space coordinates to platform space coordinates.
        
        This is an axes-swapping transformation.

        :param unified_space: Unified space coordinates.
        :type unified_space: Vector4
        :returns: Platform space coordinates.
        :rtype: Vector4
        """