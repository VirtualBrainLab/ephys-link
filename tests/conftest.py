from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ephys_link.utils.console import Console


@pytest.fixture
def mock_console(mocker: MockerFixture) -> MagicMock:
    """Fixture for Console class.

    Args:
        mocker: Mock fixture for the Console class.

    Returns:
        Mocked Console class.
    """
    return mocker.Mock(spec=Console)
