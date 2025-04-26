from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from vbl_aquarium.models.ephys_link import EphysLinkOptions

from ephys_link.back_end.platform_handler import PlatformHandler
from ephys_link.utils.base_binding import BaseBinding
from ephys_link.utils.console import Console


class TestPlatformHandler:
    """Tests for the PlatformHandler class."""

    def test_get_display_name(self, mock_console: Console, mocker: MockerFixture) -> None:
        """Platform should return binding display name.

        Args:
            mock_console: Mocked Console instance.
            mocker: Binding mocker.
        """
        # Define dummy name.
        dummy_name = "Dummy Binding"
        
        # Mock binding.
        mock_binding = mocker.Mock(spec=BaseBinding)
        mock_binding.get_display_name.return_value = dummy_name
        
        # Create PlatformHandler instance.
        platform_handler = PlatformHandler(mock_binding, mock_console)
        
        # Test.
        assert platform_handler.get_display_name() == dummy_name
