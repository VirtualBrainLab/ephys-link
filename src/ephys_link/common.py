"""Commonly used functions and dictionaries

Contains globally used helper functions and typed dictionaries (to be used as
callback parameters)
"""

from __future__ import annotations

# Debugging flag
DEBUG = False

# Ephys Link ASCII
ASCII = r"""
  ______       _                 _      _       _
 |  ____|     | |               | |    (_)     | |
 | |__   _ __ | |__  _   _ ___  | |     _ _ __ | | __
 |  __| | '_ \| '_ \| | | / __| | |    | | '_ \| |/ /
 | |____| |_) | | | | |_| \__ \ | |____| | | | |   <
 |______| .__/|_| |_|\__, |___/ |______|_|_| |_|_|\_\
        | |           __/ |
        |_|          |___/
"""


def dprint(message: str) -> None:
    """Print message if debug is enabled.

    :param message: Message to print.
    :type message: str
    :return: None
    """
    if DEBUG:
        print(message)


# Input data formats
# class GotoPositionInputDataFormat(TypedDict):
#     """Data format for positional requests.
#
#     :param manipulator_id: ID of the manipulator to move.
#     :type manipulator_id: str
#     :param pos: Position to move to in mm (X, Y, Z, W).
#     :type pos: list[float]
#     :param speed: Speed to move at in mm/s.
#     :type speed: float
#     """
#
#     manipulator_id: str
#     pos: list[float]
#     speed: float
#
#
# class InsideBrainInputDataFormat(TypedDict):
#     """Data format for setting inside brain state.
#
#     :param manipulator_id: ID of the manipulator to move.
#     :type manipulator_id: str
#     :param inside: Whether the manipulator is inside the brain.
#     :type inside: bool
#     """
#
#     manipulator_id: str
#     inside: bool
#
#
# class DriveToDepthInputDataFormat(TypedDict):
#     """Data format for depth driving requests.
#
#     :param manipulator_id: ID of the manipulator to move.
#     :type manipulator_id: str
#     :param depth: Depth to drive to in mm.
#     :type depth: float
#     :param speed: Speed to drive at in mm/s.
#     :type speed: float
#     """
#
#     manipulator_id: str
#     depth: float
#     speed: float
#
#
# class CanWriteInputDataFormat(TypedDict):
#     """Data format for setting can write state.
#
#     :param manipulator_id: ID of the manipulator to move.
#     :type manipulator_id: str
#     :param can_write: Whether the manipulator can write.
#     :type can_write: bool
#     :param hours: Number of hours the manipulator can write for.
#     :type hours: float
#     """
#
#     manipulator_id: str
#     can_write: bool
#     hours: float
#
#
# # Output data dictionaries
# class GetManipulatorsOutputData(dict):
#     """Output format for get manipulators request.
#
#     :param manipulators: List of manipulator IDs (as strings).
#     :type manipulators: list
#     :param num_axes: Number of axes this manipulator has.
#     :type num_axes: int
#     :param dimensions: Size of the movement space in mm (first 3 axes).
#     :type dimensions: list
#     :param error: Error message.
#     :type error: str
#
#     :example: Example generated dictionary
#         :code:`{"manipulators": ["1", "2"], "num_axes": 4, "dimensions": [20, 20, 20], "error": ""}`
#     """
#
#     def __init__(self, manipulators: list, num_axes: int, dimensions: list, error: str) -> None:
#         """Constructor"""
#         super().__init__(
#             manipulators=manipulators,
#             num_axes=num_axes,
#             dimensions=dimensions,
#             error=error,
#         )
#
#     def json(self) -> str:
#         """Return JSON string"""
#         return json.dumps(self)
#
#
# class PositionalOutputData(dict):
#     """Output format for positional requests.
#
#     :param position: Position in mm (as a list, empty on error) in X, Y, Z, W order.
#     :type position: list
#     :param error: Error message.
#     :type error: str
#
#     :example: Example generated dictionary
#         :code:`{"position": [10.429, 12.332, 2.131, 12.312], "error": ""}`
#     """
#
#     def __init__(self, position: list, error: str) -> None:
#         """Constructor"""
#         super().__init__(position=position, error=error)
#
#     def json(self) -> str:
#         """Return JSON string"""
#         return json.dumps(self)
#
#
# class AngularOutputData(dict):
#     """Output format for manipulator angle requests.
#
#     :param angles: Angles in degrees (as a list, can be empty) in yaw, pitch, roll order.
#     :type angles: list
#     :param error: Error message.
#     :type error: str
#     """
#
#     def __init__(self, angles: list, error: str) -> None:
#         """Constructor"""
#         super().__init__(angles=angles, error=error)
#
#     def json(self) -> str:
#         """Return JSON string"""
#         return json.dumps(self)
#
#
# class ShankCountOutputData(dict):
#     """Output format for number of shanks.
#
#     :param shank_count: Number of shanks on the probe (-1 if error).
#     :type shank_count: int
#     :param error: Error message.
#     :type error: str
#     """
#
#     def __init__(self, shank_count: int, error: str) -> None:
#         """Constructor"""
#         super().__init__(shank_count=shank_count, error=error)
#
#     def json(self) -> str:
#         """Return JSON string"""
#         return json.dumps(self)
#
#
# class DriveToDepthOutputData(dict):
#     """Output format for depth driving.
#
#     :param depth: Depth in mm (0 on error).
#     :type depth: float
#     :param error: Error message.
#     :type error: str
#
#     :example: Example generated dictionary :code:`{"depth": 1.23, "error": ""}`
#     """
#
#     def __init__(self, depth: float, error: str) -> None:
#         """Create drive to depth output data dictionary"""
#         super().__init__(depth=depth, error=error)
#
#     def json(self) -> str:
#         """Return JSON string"""
#         return json.dumps(self)
#
#
# class StateOutputData(dict):
#     """Output format for boolean state requests.
#
#     :param state: State of the event.
#     :type state: bool
#     :param error: Error message.
#     :type error: str
#
#     :example: Example generated dictionary :code:`{"state": True, "error": ""}`
#     """
#
#     def __init__(self, state: bool, error: str) -> None:
#         """Create state output data dictionary"""
#         super().__init__(state=state, error=error)
#
#     def json(self) -> str:
#         """Return JSON string"""
#         return json.dumps(self)
