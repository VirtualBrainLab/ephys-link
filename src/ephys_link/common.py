"""Commonly used functions and dictionaries

Contains globally used helper functions and typed dictionaries (to be used as
callback parameters)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vbl_aquarium.models.unity import Vector4

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


def vector4_to_array(vector4: Vector4) -> list[float]:
    """Convert a Vector4 to a list of floats.

    :param vector4: Vector4 to convert.
    :type vector4: :class:`vbl_aquarium.models.unity.Vector4`
    :return: List of floats.
    :rtype: list[float]
    """
    return [vector4.x, vector4.y, vector4.z, vector4.w]
