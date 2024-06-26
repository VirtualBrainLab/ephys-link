"""Base commands Ephys Link will support.

Definition of the commands a client to Ephys Link can expect to invoke to control manipulators.

Usage: Implement the BaseCommands class to enforce the commands Ephys Link will support.
"""

from abc import ABC, abstractmethod

from vbl_aquarium.models.ephys_link import (
    AngularResponse,
    BooleanStateResponse,
    DriveToDepthRequest,
    DriveToDepthResponse,
    GetManipulatorsResponse,
    GotoPositionRequest,
    InsideBrainRequest,
    PositionalResponse,
    ShankCountResponse,
)


class BaseCommands(ABC):
    """Base class to enforce commands Ephys Link will support."""

    @abstractmethod
    async def get_manipulators(self) -> GetManipulatorsResponse:
        """Get a list of available manipulators on the current handler.

        :returns: List of manipulator IDs, number of axes, dimensions of manipulators, and an error message if any.
        :rtype: :class:`vbl_aquarium.models.ephys_link.GetManipulatorsResponse`
        """

    @abstractmethod
    async def get_position(self, manipulator_id: str) -> PositionalResponse:
        """Get the current translation position of a manipulator in unified coordinates (mm).

        :param manipulator_id: Manipulator ID.
        :type manipulator_id: str
        :returns: Current position of the manipulator and an error message if any.
        :rtype: :class:`vbl_aquarium.models.ephys_link.PositionalResponse`
        """

    @abstractmethod
    async def get_angles(self, manipulator_id: str) -> AngularResponse:
        """Get the current rotation angles of a manipulator in Yaw, Pitch, Roll (degrees).

        :param manipulator_id: Manipulator ID.
        :type manipulator_id: str
        :returns: Current angles of the manipulator and an error message if any.
        :rtype: :class:`vbl_aquarium.models.ephys_link.AngularResponse`
        """

    @abstractmethod
    async def get_shank_count(self, manipulator_id: str) -> ShankCountResponse:
        """Get the number of shanks on a manipulator.

        :param manipulator_id: Manipulator ID.
        :type manipulator_id: str
        :returns: Number of shanks on the manipulator and an error message if any.
        :rtype: :class:`vbl_aquarium.models.ephys_link.ShankCountResponse`
        """

    @abstractmethod
    async def set_position(self, request: GotoPositionRequest) -> PositionalResponse:
        """Move a manipulator to a specified translation position in unified coordinates (mm).

        :param request: Request to move a manipulator to a specified position.
        :type request: :class:`vbl_aquarium.models.ephys_link.GotoPositionRequest`
        :returns: Final position of the manipulator and an error message if any.
        :rtype: :class:`vbl_aquarium.models.ephys_link.Position
        """

    @abstractmethod
    async def set_depth(self, request: DriveToDepthRequest) -> DriveToDepthResponse:
        """Move a manipulator's depth translation stage to a specific value (mm).

        :param request: Request to move a manipulator to a specified depth.
        :type request: :class:`vbl_aquarium.models.ephys_link.DriveToDepthRequest`
        :returns: Final depth of the manipulator and an error message if any.
        :rtype: :class:`vbl_aquarium.models.ephys_link.DriveToDepthResponse`
        """

    @abstractmethod
    async def set_inside_brain(self, request: InsideBrainRequest) -> BooleanStateResponse:
        """Mark a manipulator as inside the brain or not.

        This should restrict the manipulator's movement to just the depth axis.

        :param request: Request to set a manipulator's inside brain state.
        :type request: :class:`vbl_aquarium.models.ephys_link.InsideBrainRequest`
        :returns: Inside brain state of the manipulator and an error message if any.
        :rtype: :class:`vbl_aquarium.models.ephys_link.BooleanStateResponse`
        """

    @abstractmethod
    async def calibrate(self, manipulator_id: str) -> str:
        """Calibrate a manipulator.

        :param manipulator_id: Manipulator ID.
        :type manipulator_id: str
        :returns: Error message if any.
        :rtype: str
        """

    @abstractmethod
    async def stop(self) -> str:
        """Stop all manipulators.

        :returns: Error message if any.
        :rtype: str
        """
