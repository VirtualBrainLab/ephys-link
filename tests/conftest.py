import pytest
from vbl_aquarium.models.unity import Vector3, Vector4

from ephys_link.bindings.fake_binding import FakeBinding
from ephys_link.utils.console import Console

# Dummy values for testing.
DUMMY_STRING = "Dummy String"
DUMMY_SMALL_STRING = "dummy"
DUMMY_INT = 3
DUMMY_STRING_LIST: list[str] = [DUMMY_STRING, DUMMY_SMALL_STRING]
DUMMY_VECTOR3 = Vector3(x=1.0, y=2.0, z=3.0)
DUMMY_VECTOR4 = Vector4(x=1.0, y=2.0, z=3.0, w=4.0)
DUMMY_EXCEPTION = RuntimeError("Test runtime error")


@pytest.fixture
def test_console() -> Console:
    """Console instance for testing."""
    return Console()


@pytest.fixture
def test_fake_binding() -> FakeBinding:
    """FakeBinding instance for testing."""
    return FakeBinding()
