"""Commonly used utility functions and constants."""

from vbl_aquarium.models.unity import Vector4

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

# Unit conversions


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
