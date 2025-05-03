import asyncio
from collections.abc import Awaitable

import pytest
from pytest_mock import MockerFixture
from socketio import AsyncClient, AsyncServer  # pyright: ignore[reportMissingTypeStubs]
from vbl_aquarium.models.ephys_link import EphysLinkOptions, GetManipulatorsResponse

import ephys_link.back_end.server
from ephys_link.back_end.platform_handler import PlatformHandler
from ephys_link.back_end.server import Server
from ephys_link.front_end.console import Console
from ephys_link.utils.constants import PROXY_CLIENT_NOT_INITIALIZED_ERROR, SERVER_NOT_INITIALIZED_ERROR
from tests.conftest import DUMMY_STRING, DUMMY_STRING_LIST


class TestServer:
    @pytest.fixture
    def platform_handler(self, mocker: MockerFixture) -> PlatformHandler:
        """Fixture for mock PlatformHandler."""
        return mocker.Mock(spec=PlatformHandler)

    @pytest.fixture
    def console(self, mocker: MockerFixture) -> Console:
        """Fixture for mock console."""
        return mocker.Mock(spec=Console)

    @pytest.fixture
    def server(self, platform_handler: PlatformHandler, console: Console) -> Server:
        """Fixture for server."""
        return Server(EphysLinkOptions(use_proxy=False), platform_handler, console)

    @pytest.fixture
    def proxy_client(self, platform_handler: PlatformHandler, console: Console) -> Server:
        """Fixture for server as proxy client."""
        return Server(EphysLinkOptions(use_proxy=True), platform_handler, console)

    def test_failed_server_init(
        self, platform_handler: PlatformHandler, console: Console, mocker: MockerFixture
    ) -> None:
        """Server should raise error if sio is not an AsyncServer."""
        # Mock out the AsyncServer init.
        patched_async_server = mocker.patch.object(AsyncServer, "__new__")

        # Act
        with pytest.raises(TypeError) as init_error:
            _ = Server(EphysLinkOptions(use_proxy=False), platform_handler, console)

        # Assert
        patched_async_server.assert_called_once()
        assert init_error.value.args[0] == SERVER_NOT_INITIALIZED_ERROR

    def test_launch_server(
        self, server: Server, platform_handler: PlatformHandler, console: Console, mocker: MockerFixture
    ) -> None:
        """Server should print info then start."""
        # Add mocks and spies.
        # noinspection DuplicatedCode
        spied_info_print = mocker.spy(console, "info_print")

        patched_get_display_name = mocker.patch.object(platform_handler, "get_display_name", return_value=DUMMY_STRING)

        # Mock out get manipulators.
        patched_get_manipulators = mocker.patch.object(platform_handler, "get_manipulators", new=mocker.Mock())
        asyncio_loop = mocker.Mock()
        patched_run_until_complete = mocker.patch.object(
            asyncio_loop, "run_until_complete", return_value=GetManipulatorsResponse(manipulators=DUMMY_STRING_LIST)
        )
        patched_get_event_loop = mocker.patch.object(
            ephys_link.back_end.server, "get_event_loop", return_value=asyncio_loop
        )

        # Mock out run_app.
        mocked_run_app = mocker.patch.object(ephys_link.back_end.server, "run_app")

        # Act.
        server.launch()

        # Assert.
        patched_get_display_name.assert_called_once()
        patched_get_manipulators.assert_called_once()
        patched_run_until_complete.assert_called_once()
        patched_get_event_loop.assert_called_once()
        spied_info_print.assert_any_call("PLATFORM", platform_handler.get_display_name())
        spied_info_print.assert_any_call("MANIPULATORS", str(DUMMY_STRING_LIST))
        mocked_run_app.assert_called_once()

    def test_launch_proxy_client(
        self, proxy_client: Server, platform_handler: PlatformHandler, console: Console, mocker: MockerFixture
    ) -> None:
        """Proxy client should print info then start."""
        # Add mocks and spies.
        # noinspection DuplicatedCode
        spied_info_print = mocker.spy(console, "info_print")

        patched_get_display_name = mocker.patch.object(platform_handler, "get_display_name", return_value=DUMMY_STRING)

        # Mock out get manipulators.
        patched_get_manipulators = mocker.patch.object(platform_handler, "get_manipulators", new=mocker.Mock())
        asyncio_loop = mocker.Mock()
        patched_run_until_complete = mocker.patch.object(
            asyncio_loop, "run_until_complete", return_value=GetManipulatorsResponse(manipulators=DUMMY_STRING_LIST)
        )
        patched_get_event_loop = mocker.patch.object(
            ephys_link.back_end.server, "get_event_loop", return_value=asyncio_loop
        )

        # Mock out run.
        def run_coroutine(coroutine: Awaitable[None]) -> None:
            """Run the coroutine."""
            asyncio.new_event_loop().run_until_complete(coroutine)

        _ = mocker.patch.object(ephys_link.back_end.server, "run", new=run_coroutine)
        patched_connect = mocker.patch.object(AsyncClient, "connect", new_callable=mocker.AsyncMock)
        patched_wait = mocker.patch.object(AsyncClient, "wait", new_callable=mocker.AsyncMock)

        # Act.
        proxy_client.launch()

        # Assert.
        patched_get_display_name.assert_called_once()
        patched_get_manipulators.assert_called_once()
        patched_run_until_complete.assert_called_once()
        patched_get_event_loop.assert_called_once()
        spied_info_print.assert_any_call("PLATFORM", platform_handler.get_display_name())
        spied_info_print.assert_any_call("MANIPULATORS", str(DUMMY_STRING_LIST))
        spied_info_print.assert_any_call("PINPOINT ID", mocker.ANY)  # pyright: ignore[reportAny]
        patched_connect.assert_awaited_once()  # pyright: ignore[reportUnusedCallResult]
        patched_wait.assert_awaited_once()  # pyright: ignore[reportUnusedCallResult]

    def test_launch_proxy_client_failed_init(
        self, platform_handler: PlatformHandler, console: Console, mocker: MockerFixture
    ) -> None:
        """Proxy client should print info then start."""
        # Add mocks and spies.
        # noinspection DuplicatedCode
        spied_info_print = mocker.spy(console, "info_print")

        patched_get_display_name = mocker.patch.object(platform_handler, "get_display_name", return_value=DUMMY_STRING)

        # Mock out get manipulators.
        patched_get_manipulators = mocker.patch.object(platform_handler, "get_manipulators", new=mocker.Mock())
        asyncio_loop = mocker.Mock()
        patched_run_until_complete = mocker.patch.object(
            asyncio_loop, "run_until_complete", return_value=GetManipulatorsResponse(manipulators=DUMMY_STRING_LIST)
        )
        patched_get_event_loop = mocker.patch.object(
            ephys_link.back_end.server, "get_event_loop", return_value=asyncio_loop
        )

        # Mock out run.
        def run_coroutine(coroutine: Awaitable[None]) -> None:
            """Run the coroutine."""
            asyncio.new_event_loop().run_until_complete(coroutine)

        _ = mocker.patch.object(ephys_link.back_end.server, "run", new=run_coroutine)
        patched_connect = mocker.patch.object(AsyncClient, "connect", new_callable=mocker.AsyncMock)
        patched_wait = mocker.patch.object(AsyncClient, "wait", new_callable=mocker.AsyncMock)

        # Mock out the AsyncServer init.
        patched_async_server = mocker.patch.object(AsyncClient, "__new__")

        # Act
        with pytest.raises(TypeError) as init_error:
            Server(EphysLinkOptions(use_proxy=True), platform_handler, console).launch()

        # Assert.
        patched_async_server.assert_called_once()
        patched_get_display_name.assert_called_once()
        patched_get_manipulators.assert_called_once()
        patched_run_until_complete.assert_called_once()
        patched_get_event_loop.assert_called_once()
        spied_info_print.assert_any_call("PLATFORM", platform_handler.get_display_name())
        spied_info_print.assert_any_call("MANIPULATORS", str(DUMMY_STRING_LIST))
        spied_info_print.assert_any_call("PINPOINT ID", mocker.ANY)  # pyright: ignore[reportAny]
        assert init_error.value.args[0] == PROXY_CLIENT_NOT_INITIALIZED_ERROR
        patched_connect.assert_not_awaited()  # pyright: ignore[reportUnusedCallResult]
        patched_wait.assert_not_awaited()  # pyright: ignore[reportUnusedCallResult]
