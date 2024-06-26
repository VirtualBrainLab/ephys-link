"""Commonly used utility functions and constants."""

from os.path import join
from pathlib import Path

from vbl_aquarium.models.unity import Vector4

# Ephys Link ASCII.
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

# Absolute path to the resources folder.
RESOURCES_PATH = join(str(Path(__file__).parent.absolute()), "resources")

# Unit conversions


def mmps_to_umps(mmps: float) -> float:
    """Convert millimeters per second to micrometers per second.

    :param mmps: Speed in millimeters per second.
    :type mmps: float
    :returns: Speed in micrometers per second.
    :rtype: float
    """
    return mmps * 1_000


def mm_to_um(mm: Vector4) -> Vector4:
    """Convert millimeters to micrometers.

    :param mm: Length in millimeters.
    :type mm: Vector4
    :returns: Length in micrometers.
    :rtype: Vector4
    """
    return mm * 1_000


def um_to_mm(um: Vector4) -> Vector4:
    """Convert micrometers to millimeters.

    :param um: Length in micrometers.
    :type um: Vector4
    :returns: Length in millimeters.
    :rtype: Vector4
    """
    return um / 1_000


def vector4_to_array(vector4: Vector4) -> list[float]:
    """Convert a Vector4 to a list of floats.

    :param vector4: Vector4 to convert.
    :type vector4: :class:`vbl_aquarium.models.unity.Vector4`
    :return: List of floats.
    :rtype: list[float]
    """
    return [vector4.x, vector4.y, vector4.z, vector4.w]


def array_to_vector4(array: list[float]) -> Vector4:
    """Convert a list of floats to a Vector4.

    :param array: List of floats.
    :type array: list[float]
    :return: First four elements of the list as a Vector4 padded with zeros if necessary.
    :rtype: :class:`vbl_aquarium.models.unity.Vector4`
    """

    def get_element(array: list[float], index: int) -> float:
        try:
            return array[index]
        except IndexError:
            return 0.0

    return Vector4(
        x=get_element(array, 0),
        y=get_element(array, 1),
        z=get_element(array, 2),
        w=get_element(array, 3),
    )
