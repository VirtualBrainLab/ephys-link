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
class PositionalOutputData(dict):
    """Position data format"""

    def __init__(self, manipulator_id: int, position: tuple, error: str):
        super(PositionalOutputData, self). \
            __init__(self, manipulator_id=manipulator_id,
                     position=position,
                     error=error)
