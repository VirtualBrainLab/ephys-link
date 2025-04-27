import pytest

from ephys_link.bindings.fake_binding import FakeBinding
from ephys_link.utils.console import Console


@pytest.fixture
def test_console() -> Console:
    """Console instance for testing."""
    return Console()


@pytest.fixture
def test_fake_binding() -> FakeBinding:
    """FakeBinding instance for testing."""
    return FakeBinding()
