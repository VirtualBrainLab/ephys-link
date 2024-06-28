from collections.abc import Callable, Coroutine
from json import JSONDecodeError, dumps, loads
from typing import Any

from aiohttp.web import Application
from pydantic import ValidationError
from socketio import AsyncClient, AsyncServer
from vbl_aquarium.models.ephys_link import (
    DriveToDepthRequest,
    EphysLinkOptions,
    GotoPositionRequest,
)
from vbl_aquarium.models.generic import VBLBaseModel

from ephys_link.back_end.platform_handler import PlatformHandler
from ephys_link.util.console import Console


class Server:
    def __init__(self, options: EphysLinkOptions, platform_handler: PlatformHandler, console: Console) -> None:
        """Initialize server fields based on options and platform handler."""

        # Initialize based on proxy usage.
        if options.use_proxy:
            self._sio = AsyncClient()
        else:
            self._sio = AsyncServer()
            self._app = Application()
            self._sio.attach(self._app)

            # Bind connection events.
            self._sio.on("connect", self.connect)
            self._sio.on("disconnect", self.disconnect)

        # Platform handler.
        self._platform_handler = platform_handler

        # Console.
        self._console = console

        # Store connected client.
        self._client_sid: str = ""

        # Bind events.
        self._sio.on("*", self.platform_event_handler)

    # Server launch.
    def launch(self) -> None:
        self._console.info_print("SERVER", "Starting server...")

    # Helper functions.
    def _malformed_request_response(self, request: str, data: str) -> str:
        """Return a response for a malformed request."""
        self._console.labeled_error_print("MALFORMED REQUEST", f"{request}: {data}")
        return dumps({"error": "Malformed request."})

    async def _run_if_data_available(
        self, function: Callable[[str], Coroutine[Any, Any, VBLBaseModel]], event: str, data: str
    ) -> str:
        """Run a function if data is available."""
        if data:
            return (await function(data)).to_string()
        return self._malformed_request_response(event, data)

    async def _run_if_data_parses(
        self,
        function: Callable[[VBLBaseModel], Coroutine[Any, Any, VBLBaseModel]],
        data_type: type[VBLBaseModel],
        event: str,
        data: str,
    ) -> str:
        """Run a function if data parses."""
        if data:
            try:
                parsed_data = data_type(**loads(data))
            except JSONDecodeError:
                return self._malformed_request_response(event, data)
            except ValidationError as e:
                self._console.exception_error_print(event, e)
                return self._malformed_request_response(event, data)
            else:
                return (await function(parsed_data)).to_string()
        return self._malformed_request_response(event, data)

    # Event Handlers.

    async def connect(self, sid: str) -> bool:
        """Handle connections to the server

        :param sid: Socket session ID.
        :type sid: str
        :returns: False on error to refuse connection, True otherwise.
        :rtype: bool
        """
        self._console.info_print("CONNECTION REQUEST", sid)

        if self._client_sid == "":
            self._client_sid = sid
            self._console.info_print("CONNECTION GRANTED", sid)
            return True

        self._console.error_print(f"CONNECTION REFUSED to {sid}. Client {self._client_sid} already connected.")
        return False

    async def disconnect(self, sid: str) -> None:
        """Handle disconnections from the server

        :param sid: Socket session ID.
        :type sid: str
        """
        self._console.info_print("DISCONNECTED", sid)

        # Reset client SID if it matches.
        if self._client_sid == sid:
            self._client_sid = ""
        else:
            self._console.error_print(f"Client {sid} disconnected without being connected.")

    async def platform_event_handler(self, event: str, sid: str, data: str) -> str:
        """Handle events from the server

        :param event: Event name.
        :type event: str
        :param sid: Socket session ID.
        :type sid: str
        :param data: Event data.
        :type data: str
        :returns: Response data.
        :rtype: str
        """

        # Ignore events from SID's that don't match the client.
        if sid != self._client_sid:
            self._console.error_print(f"Event from unauthorized client {sid}.")
            return "ERROR"

        # Log event.
        self._console.debug_print("EVENT", event)

        # Handle event.
        match event:
            # Server metadata.
            case "get_version":
                return await self._platform_handler.get_version()
            case "get_pinpoint_id":
                return (await self._platform_handler.get_pinpoint_id()).to_string()
            case "get_platform_type":
                return await self._platform_handler.get_platform_type()

            # Manipulator commands.
            case "get_manipulators":
                return (await self._platform_handler.get_manipulators()).to_string()
            case "get_position":
                return await self._run_if_data_available(self._platform_handler.get_position, event, data)
            case "get_angles":
                return await self._run_if_data_available(self._platform_handler.get_angles, event, data)
            case "get_shank_count":
                return await self._run_if_data_available(self._platform_handler.get_shank_count, event, data)
            case "set_position":
                return await self._run_if_data_parses(
                    self._platform_handler.set_position, GotoPositionRequest, event, data
                )
            case "set_depth":
                return await self._run_if_data_parses(
                    self._platform_handler.set_depth, DriveToDepthRequest, event, data
                )

        return "OK"
