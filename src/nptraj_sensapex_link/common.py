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


# Output data formats
class IdOutputData(dict):
    """Output format for (id, error)"""

    def __init__(self, manipulator_id: int, error: str) -> None:
        """
        Create ID output data dictionary
        :param manipulator_id: Manipulator ID
        :param error: Error message
        """
        super(IdOutputData, self).__init__(manipulator_id=manipulator_id,
                                           error=error)


class PositionalOutputData(dict):
    """Output format for (id, position, error) format"""

    def __init__(self, manipulator_id: int, position: tuple, error: str) -> \
            None:
        """
        Create positional output data dictionary
        :param manipulator_id: Manipulator ID
        :param position: Position (as a tuple, can be empty tuple)
        :param error: Error message
        """
        super(PositionalOutputData, self). \
            __init__(manipulator_id=manipulator_id,
                     position=position,
                     error=error)
