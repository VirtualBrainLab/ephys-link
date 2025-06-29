from io import StringIO
import sys

import pytest
from pytest_mock import MockerFixture

from ephys_link.__about__ import __version__
from ephys_link.front_end.console import Console
from ephys_link.utils.constants import ASCII, UNABLE_TO_CHECK_FOR_UPDATES_ERROR
from ephys_link.utils.startup import preamble, check_for_updates

from requests import ConnectionError

class TestStartup:
    @pytest.fixture
    def console(self, mocker: MockerFixture) -> Console:
        """Fixture for mock console."""
        return mocker.Mock(spec=Console)
    
    def test_preamble(self) -> None:
        """Test the preamble function."""
        # Arrange.
        captured_output = StringIO()
        sys.stdout = captured_output

        # Act.
        preamble()

        # Assert.
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        assert "Ephys Link" in output
        assert "This is the Ephys Link server window." in output
        assert __version__ in output
        assert ASCII in output
    
    def test_check_for_updates_is_newer(self, console: Console, mocker: MockerFixture) -> None:
        """Test the check_for_updates function."""
        # Add mocks and spies.
        spied_critical_print = mocker.spy(console, "critical_print")

        # Mock requests.get to return a fake response with a lower version.
        fake_response = mocker.Mock()
        fake_response.json.return_value = [{"name": "0.0.0"}]
        mocker.patch("ephys_link.utils.startup.get", return_value=fake_response)

        # Act
        check_for_updates(console)

        # Assert: critical_print should NOT be called since no update is available.
        spied_critical_print.assert_not_called()
        
    def test_check_for_updates_is_older(self, console: Console, mocker: MockerFixture) -> None:
        """Test the check_for_updates function with a newer version."""
        # Add mocks and spies.
        spied_critical_print = mocker.spy(console, "critical_print")

        # Mock the json() method of the response from get
        fake_response = mocker.Mock()
        fake_response.json.return_value = [{"name": "1000000.0.0"}]
        mocker.patch("ephys_link.utils.startup.get", return_value=fake_response)

        # Act
        check_for_updates(console)

        # Assert: critical_print should be called since an update is available.
        spied_critical_print.assert_called()
    
    def test_check_for_updates_connection_error(self, console: Console, mocker: MockerFixture) -> None:
        """Test the check_for_updates function with a connection error."""
        # Add mocks and spies.
        spied_error_print = mocker.spy(console, "error_print")

        # Mock requests.get to raise a ConnectionError.
        mocker.patch("ephys_link.utils.startup.get", side_effect=ConnectionError)

        # Act
        check_for_updates(console)

        # Assert: error_print should be called with the correct message.
        spied_error_print.assert_called_with(
            "UPDATE", UNABLE_TO_CHECK_FOR_UPDATES_ERROR
        )
    
    def test_check_for_updates_connect_timeout(self, console: Console, mocker: MockerFixture) -> None:
        """Test the check_for_updates function with a connect timeout."""
        # Add mocks and spies.
        spied_error_print = mocker.spy(console, "error_print")

        # Mock requests.get to raise a ConnectTimeout.
        mocker.patch("ephys_link.utils.startup.get", side_effect=ConnectionError)

        # Act
        check_for_updates(console)

        # Assert: error_print should be called with the correct message.
        spied_error_print.assert_called_with(
            "UPDATE", UNABLE_TO_CHECK_FOR_UPDATES_ERROR
        )
