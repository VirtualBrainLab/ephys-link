"""Commonly used conversion functions."""

from vbl_aquarium.models.unity import Vector4


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


def list_to_vector4(float_list: list[float | int]) -> Vector4:
    """Convert a list of floats to a [Vector4][vbl_aquarium.models.unity.Vector4].

    Args:
        float_list: List of floats.

    Returns:
        First four elements of the list as a Vector4 padded with zeros if necessary.
    """

    def get_element(this_array: list[float | int], index: int) -> float:
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
        x=get_element(float_list, 0),
        y=get_element(float_list, 1),
        z=get_element(float_list, 2),
        w=get_element(float_list, 3),
    )
