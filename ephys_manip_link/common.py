from typing import TypedDict

# Debugging stuff
DEBUG = False


def set_debug(debug: bool) -> None:
    """
    Set debug flag
    :param debug: True to enable debug mode, False to disable
    :return: None
    """
    global DEBUG
    DEBUG = debug


def dprint(message: str) -> None:
    """
    Print message if debug is enabled
    :param message: Message to print
    :return: None
    """
    if DEBUG:
        print(message)


# Input data formats
class GotoPositionInputDataFormat(TypedDict):
    """Data format for goto_pos"""

    manipulator_id: int
    pos: list[float]
    speed: int


class InsideBrainInputDataFormat(TypedDict):
    """Data format for inside_brain"""

    manipulator_id: int
    inside: bool


class DriveToDepthInputDataFormat(TypedDict):
    """Data format for drive_to_depth"""

    manipulator_id: int
    depth: float
    speed: int


class CanWriteInputDataFormat(TypedDict):
    """Data format for can_write"""

    manipulator_id: int
    can_write: bool
    hours: float


# Output data dictionaries
class GetManipulatorsOutputData(dict):
    """Output format for (manipulators)"""

    def __init__(self, manipulators: list, error: str) -> None:
        """
        :param manipulators: Tuple of manipulator IDs
        """
        super(GetManipulatorsOutputData, self).__init__(
            manipulators=manipulators, error=error
        )


class PositionalOutputData(dict):
    """Output format for (id, position, error)"""

    def __init__(self, position: list, error: str) -> None:
        """
        Create positional output data dictionary
        :param position: Position (as a tuple, can be empty tuple)
        :param error: Error message
        """
        super(PositionalOutputData, self).__init__(position=position, error=error)


class DriveToDepthOutputData(dict):
    """Output format for depth driving (id, depth, error)"""

    def __init__(self, depth: float, error: str) -> None:
        """
        Create drive to depth output data dictionary
        :param depth: Depth
        :param error: Error message
        """
        super(DriveToDepthOutputData, self).__init__(depth=depth, error=error)


class StateOutputData(dict):
    """Output format for (id, state, error)"""

    def __init__(self, state: bool, error: str) -> None:
        """
        Create state output data dictionary
        :param state: State of the event
        :param error: Error message
        """
        super(StateOutputData, self).__init__(state=state, error=error)
