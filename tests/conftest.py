import pytest
from pytest_mock import MockerFixture
from vbl_aquarium.models.unity import Vector3, Vector4

from ephys_link.front_end.console import Console
from ephys_link.utils.base_binding import BaseBinding

# Dummy values for testing.
DUMMY_STRING = "Dummy String"
DUMMY_SMALL_STRING = "dummy"
DUMMY_INT = 3
DUMMY_STRING_LIST: list[str] = [DUMMY_STRING, DUMMY_SMALL_STRING]
DUMMY_VECTOR3 = Vector3(x=1.0, y=2.0, z=3.0)
DUMMY_VECTOR4 = Vector4(x=1.0, y=2.0, z=3.0, w=4.0)
DUMMY_EXCEPTION = RuntimeError("Test runtime error")


@pytest.fixture
def console() -> Console:
    """Console instance for testing."""
    return Console()


@pytest.fixture
def binding(mocker: MockerFixture) -> BaseBinding:
    """FakeBinding instance for testing."""

    def reflect_vector4(input_vector: Vector4) -> Vector4:
        return input_vector

    # Patch the BaseBinding class.
    mocked_binding = mocker.Mock(spec=BaseBinding)
    _ = mocker.patch.object(mocked_binding, "platform_space_to_unified_space", side_effect=reflect_vector4)
    _ = mocker.patch.object(mocked_binding, "unified_space_to_platform_space", side_effect=reflect_vector4)
    return mocked_binding
