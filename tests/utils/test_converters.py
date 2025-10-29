"""Unit tests for converters.py with 100% coverage."""

from vbl_aquarium.models.unity import Vector4

from ephys_link.utils.converters import list_to_vector4, scalar_mm_to_um, um_to_mm, vector4_to_array, vector_mm_to_um
from tests.conftest import DUMMY_VECTOR4


class TestConverters:
    """Test class for converters module with 100% coverage."""

    def test_scalar_mm_to_um_positive(self):
        """Test scalar mm to um conversion with positive value."""
        result = scalar_mm_to_um(5.5)
        assert result == 5500.0

    def test_scalar_mm_to_um_negative(self):
        """Test scalar mm to um conversion with negative value."""
        result = scalar_mm_to_um(-2.3)
        assert result == -2300.0

    def test_scalar_mm_to_um_zero(self):
        """Test scalar mm to um conversion with zero."""
        result = scalar_mm_to_um(0.0)
        assert result == 0.0

    def test_vector_mm_to_um(self):
        """Test vector mm to um conversion using dummy vector."""
        # DUMMY_VECTOR4 is Vector4(x=1.0, y=2.0, z=3.0, w=4.0)
        result = vector_mm_to_um(DUMMY_VECTOR4)
        expected = Vector4(x=1000.0, y=2000.0, z=3000.0, w=4000.0)

        assert result == expected

    def test_vector_mm_to_um_with_zeros(self):
        """Test vector mm to um conversion with zero values."""
        input_vector = Vector4(x=0.0, y=5.0, z=0.0, w=-1.0)
        result = vector_mm_to_um(input_vector)
        expected = Vector4(x=0.0, y=5000.0, z=0.0, w=-1000.0)

        assert result == expected

    def test_um_to_mm(self):
        """Test um to mm conversion."""
        input_vector = Vector4(x=1000.0, y=2000.0, z=3000.0, w=4000.0)
        result = um_to_mm(input_vector)
        expected = Vector4(x=1.0, y=2.0, z=3.0, w=4.0)

        assert result == expected

    def test_um_to_mm_with_decimals(self):
        """Test um to mm conversion with decimal results."""
        input_vector = Vector4(x=500.0, y=1500.0, z=2500.0, w=3500.0)
        result = um_to_mm(input_vector)
        expected = Vector4(x=0.5, y=1.5, z=2.5, w=3.5)

        assert result == expected

    def test_vector4_to_array(self):
        """Test Vector4 to array conversion using dummy vector."""
        # DUMMY_VECTOR4 is Vector4(x=1.0, y=2.0, z=3.0, w=4.0)
        result = vector4_to_array(DUMMY_VECTOR4)

        assert result == [1.0, 2.0, 3.0, 4.0]
        assert isinstance(result, list)
        assert all(isinstance(x, float) for x in result)

    def test_vector4_to_array_with_negative_values(self):
        """Test Vector4 to array conversion with negative values."""
        input_vector = Vector4(x=-1.0, y=0.0, z=5.0, w=-10.0)
        result = vector4_to_array(input_vector)

        assert result == [-1.0, 0.0, 5.0, -10.0]

    def test_list_to_vector4_exact_four_elements(self):
        """Test list to Vector4 conversion with exactly 4 elements."""
        float_list = [1.0, 2.0, 3.0, 4.0]
        result = list_to_vector4(float_list)
        expected = Vector4(x=1.0, y=2.0, z=3.0, w=4.0)

        assert result == expected

    def test_list_to_vector4_less_than_four_elements(self):
        """Test list to Vector4 conversion with less than 4 elements (padding with zeros)."""
        # Test with 3 elements
        float_list = [1.0, 2.0, 3.0]
        result = list_to_vector4(float_list)
        assert result == Vector4(x=1.0, y=2.0, z=3.0, w=0.0)

        # Test with 2 elements
        float_list = [5.0, 6.0]
        result = list_to_vector4(float_list)
        assert result == Vector4(x=5.0, y=6.0, z=0.0, w=0.0)

        # Test with 1 element
        float_list = [7.0]
        result = list_to_vector4(float_list)
        assert result == Vector4(x=7.0, y=0.0, z=0.0, w=0.0)

    def test_list_to_vector4_empty_list(self):
        """Test list to Vector4 conversion with empty list (all zeros)."""
        float_list: list[float] = []
        result = list_to_vector4(float_list)
        expected = Vector4(x=0.0, y=0.0, z=0.0, w=0.0)

        assert result == expected

    def test_list_to_vector4_more_than_four_elements(self):
        """Test list to Vector4 conversion with more than 4 elements (ignores extra)."""
        float_list = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        result = list_to_vector4(float_list)
        expected = Vector4(x=1.0, y=2.0, z=3.0, w=4.0)

        assert result == expected

    def test_list_to_vector4_with_integers(self):
        """Test list to Vector4 conversion with integer inputs."""
        int_list = [1, 2, 3, 4]
        result = list_to_vector4(int_list)  # pyright: ignore[reportArgumentType]
        expected = Vector4(x=1.0, y=2.0, z=3.0, w=4.0)

        assert result == expected

        # Verify they're floats in the Vector4
        assert isinstance(result.x, float)
        assert isinstance(result.y, float)
        assert isinstance(result.z, float)
        assert isinstance(result.w, float)

    def test_list_to_vector4_mixed_types(self):
        """Test list to Vector4 conversion with mixed int and float types."""
        mixed_list = [1, 2.5, 3, 4.5]
        result = list_to_vector4(mixed_list)
        expected = Vector4(x=1.0, y=2.5, z=3.0, w=4.5)

        assert result == expected
