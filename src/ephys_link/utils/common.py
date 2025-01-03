# ruff: noqa: T201
"""Commonly used utility functions and constants."""

from os.path import abspath, dirname, join

from packaging.version import parse
from requests import ConnectionError, ConnectTimeout, get
from vbl_aquarium.models.unity import Vector4

from ephys_link.__about__ import __version__

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

# Absolute path to the resource folder.
PACKAGE_DIRECTORY = dirname(dirname(abspath(__file__)))
RESOURCES_DIRECTORY = join(PACKAGE_DIRECTORY, "resources")
BINDINGS_DIRECTORY = join(RESOURCES_DIRECTORY, "bindings")

# Ephys Link Port
PORT = 3000


# Server startup.
def server_preamble() -> None:
    """Print the server startup preamble."""
    print(ASCII)
    print(__version__)
    print()
    print("This is the Ephys Link server window.")
    print("You may safely leave it running in the background.")
    print("To stop it, close this window or press CTRL + Pause/Break.")
    print()


def check_for_updates() -> None:
    """Check for updates to the Ephys Link."""
    try:
        response = get("https://api.github.com/repos/VirtualBrainLab/ephys-link/tags", timeout=10)
        latest_version = response.json()[0]["name"]
        if parse(latest_version) > parse(__version__):
            print(f"Update available: {latest_version} !")
            print("Download at: https://github.com/VirtualBrainLab/ephys-link/releases/latest")
    except (ConnectionError, ConnectTimeout):
        print("Unable to check for updates. Ignore updates or use the the -i flag to disable checks.\n")


# Unit conversions


def scalar_mm_to_um(mm: float) -> float:
    """Convert scalar values of millimeters to micrometers.

    Args:
        mm: Scalar value in millimeters.

    Returns:
        Scalar value in micrometers.
    """
    return mm * 1_000


def vector_mm_to_um(mm: Vector4) -> Vector4:
    """Convert vector values of millimeters to micrometers.

    Args:
        mm: Vector in millimeters.

    Returns:
        Vector in micrometers.
    """
    return mm * 1_000


def um_to_mm(um: Vector4) -> Vector4:
    """Convert micrometers to millimeters.

    Args:
        um: Length in micrometers.

    Returns:
        Length in millimeters.
    """
    return um / 1_000


def vector4_to_array(vector4: Vector4) -> list[float]:
    """Convert a [Vector4][vbl_aquarium.models.unity.Vector4] to a list of floats.

    Args:
        vector4: [Vector4][vbl_aquarium.models.unity.Vector4] to convert.

    Returns:
        List of floats.
    """
    return [vector4.x, vector4.y, vector4.z, vector4.w]


def array_to_vector4(array: list[float]) -> Vector4:
    """Convert a list of floats to a [Vector4][vbl_aquarium.models.unity.Vector4].

    Args:
        array: List of floats.

    Returns:
        First four elements of the list as a Vector4 padded with zeros if necessary.
    """

    def get_element(this_array: list[float], index: int) -> float:
        """Safely get an element from an array.

        Return 0 if the index is out of bounds.

        Args:
            this_array: Array to get the element from.
            index: Index to get.

        Returns:
            Element at the index or 0 if the index is out of bounds.
        """
        try:
            return this_array[index]
        except IndexError:
            return 0.0

    return Vector4(
        x=get_element(array, 0),
        y=get_element(array, 1),
        z=get_element(array, 2),
        w=get_element(array, 3),
    )
