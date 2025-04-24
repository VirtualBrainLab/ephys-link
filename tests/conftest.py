from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture


@pytest.fixture
def mock_console(mocker: MockerFixture) -> MagicMock:
    """Fixture for Console class.

    Args:
        mocker: Mock fixture for the Console class.

    Returns:
        Mocked Console class.
    """
    return mocker.MagicMock()
