"""Commonly used functions and dictionaries

Contains globally used helper functions and typed dictionaries (to be used as
callback parameters)
"""

from typing import TypedDict

# Debugging flag
DEBUG = False


def set_debug(debug: bool) -> None:
    """Set debug flag

    :param debug: True to enable debug mode, False to disable
    :type debug: bool
    :return: None
    """
    global DEBUG
    DEBUG = debug


def dprint(message: str) -> None:
    """Print message if debug is enabled

    :param message: Message to print
    :type message: str
    :return: None
    """
    if DEBUG:
        print(message)


# Input data formats
class GotoPositionInputDataFormat(TypedDict):
    """Data format for :func:`server.goto_pos`"""

    manipulator_id: int
    pos: list[float]
    speed: int


class InsideBrainInputDataFormat(TypedDict):
    """Data format for :func:`server.set_inside_brain`"""

    manipulator_id: int
    inside: bool


class DriveToDepthInputDataFormat(TypedDict):
    """Data format for :func:`server.drive_to_depth`"""

    manipulator_id: int
    depth: float
    speed: int


class CanWriteInputDataFormat(TypedDict):
    """Data format for :func:`server.set_can_write`"""

    manipulator_id: int
    can_write: bool
    hours: float


# Output data dictionaries
class GetManipulatorsOutputData(dict):
    """Output format for (manipulators)

    :param manipulators: Tuple of manipulator IDs
    :type manipulators: list
    :param error: Error message
    :type error: str

    :example: Example generated dictionary
        :code:`{"manipulators": [1, 2], "error": ""}`
    """

    def __init__(self, manipulators: list, error: str) -> None:
        """Constructor"""
        super(GetManipulatorsOutputData, self).__init__(
            manipulators=manipulators, error=error
        )


class PositionalOutputData(dict):
    """Output format for (position, error)

    :param position: Position in mm (as a tuple, can be empty tuple)
    :type position: list
    :param error: Error message
    :type error: str

    :example: Example generated dictionary
        :code:`{"position": [10429, 12332, 2131, 12312], "error": ""}`
    """

    def __init__(self, position: list, error: str) -> None:
        """Constructor"""
        super(PositionalOutputData, self).__init__(position=position, error=error)


class DriveToDepthOutputData(dict):
    """Output format for depth driving (depth, error)

    :param depth: Depth
    :type depth: float
    :param error: Error message
    :type error: str

    :example: Example generated dictionary :code:`{"depth": 123, "error": ""}`
    """

    def __init__(self, depth: float, error: str) -> None:
        """Create drive to depth output data dictionary"""
        super(DriveToDepthOutputData, self).__init__(depth=depth, error=error)


class StateOutputData(dict):
    """Output format for (state, error)

    :param state: State of the event
    :type state: bool
    :param error: Error message
    :type error: str

    :example: Example generated dictionary :code:`{"state": True, "error": ""}`
    """

    def __init__(self, state: bool, error: str) -> None:
        """Create state output data dictionary"""
        super(StateOutputData, self).__init__(state=state, error=error)
