"""WebSocket server and communication handler

Manages the WebSocket server and handles connections and events from the client. For
every event, the server does the following:

1. Extract the arguments passed in the event
2. Log that the event was received
3. Call the appropriate function in :mod:`ephys_link.sensapex_handler` with arguments
4. Relay the response from :mod:`ephys_link.sensapex_handler` to the callback function
"""

import importlib
import sys
from typing import Any

import socketio
from aiohttp import web
from aiohttp.web_runner import GracefulExit
from pythonnet import load

from ephys_link import common as com
from ephys_link.__about__ import __version__ as version
from ephys_link.platform_handler import PlatformHandler

# Setup server
load("netfx")


class Server:
    def __init__(self):
        # Server and Socketio
        self.sio = socketio.AsyncServer()
        self.app = web.Application()

        # Is there a client connected?
        self.is_connected = False

        # Is the server running?
        self.is_running = False

        # Current platform handler (default to generic)
        self.platform: PlatformHandler = PlatformHandler()

        # Attach server to the web app
        self.sio.attach(self.app)

        # Declare events
        self.sio.on("connect", self.connect)
        self.sio.on("disconnect", self.disconnect)
        self.sio.on("get_version", self.get_version)
        self.sio.on("get_manipulators", self.get_manipulators)
        self.sio.on("register_manipulator", self.register_manipulator)
        self.sio.on("unregister_manipulator", self.unregister_manipulator)
        self.sio.on("get_pos", self.get_pos)
        self.sio.on("get_angles", self.get_angles)
        self.sio.on("get_shank_count", self.get_shank_count)
        self.sio.on("goto_pos", self.goto_pos)
        self.sio.on("drive_to_depth", self.drive_to_depth)
        self.sio.on("set_inside_brain", self.set_inside_brain)
        self.sio.on("calibrate", self.calibrate)
        self.sio.on("bypass_calibration", self.bypass_calibration)
        self.sio.on("set_can_write", self.set_can_write)
        self.sio.on("stop", self.stop)
        self.sio.on("*", self.catch_all)

    async def connect(self, sid, _, __) -> bool:
        """Acknowledge connection to the server

        :param sid: Socket session ID
        :type sid: str
        :param _: WSGI formatted dictionary with request info (unused)
        :type _: dict
        :param __: Authentication details (unused)
        :type __: dict
        :return: False on error to refuse connection. True otherwise.
        :rtype: bool
        """
        print(f"[CONNECTION REQUEST]:\t\t {sid}\n")

        if not self.is_connected:
            print(f"[CONNECTION GRANTED]:\t\t {sid}\n")
            self.is_connected = True
            return True

        print(f"[CONNECTION DENIED]:\t\t {sid}: another client is already connected\n")
        return False

    async def disconnect(self, sid) -> None:
        """Acknowledge disconnection from the server

        :param sid: Socket session ID
        :type sid: str
        :return: None
        """
        print(f"[DISCONNECTION]:\t {sid}\n")

        self.platform.reset()
        self.is_connected = False

    # Events

    @staticmethod
    async def get_version(_) -> str:
        """Get the version number of the server

        :param _: Socket session ID (unused)
        :type _: str
        :return: Version number as defined in __version__
        :rtype: str
        """
        return version

    async def get_manipulators(self, _) -> str:
        """Get the list of discoverable manipulators

        :param _: Socket session ID (unused)
        :type _: str
        :return: Callback as :class:`ephys_link.common.GetManipulatorsOutputData`
        :rtype: str
        """
        com.dprint("[EVENT]\t\t Get discoverable manipulators")

        return self.platform.get_manipulators().json()

    async def register_manipulator(self, _, manipulator_id: str) -> str:
        """Register a manipulator with the server

        :param _: Socket session ID (unused)
        :type _: str
        :param manipulator_id: ID of the manipulator to register
        :type manipulator_id: str
        :return: Error message (on error)
        :rtype: str
        """
        com.dprint(f"[EVENT]\t\t Register manipulator: {manipulator_id}")

        return self.platform.register_manipulator(manipulator_id)

    async def unregister_manipulator(self, _, manipulator_id: str) -> str:
        """Unregister a manipulator from the server

        :param _: Socket session ID (unused)
        :type _: str
        :param manipulator_id: ID of the manipulator to unregister
        :type manipulator_id: str
        :return: Error message (on error)
        :rtype: str
        """
        com.dprint(f"[EVENT]\t\t Unregister manipulator: {manipulator_id}")

        return self.platform.unregister_manipulator(manipulator_id)

    async def get_pos(self, _, manipulator_id: str) -> str:
        """Position of manipulator request

        :param _: Socket session ID (unused)
        :type _: str
        :param manipulator_id: ID of manipulator to pull position from
        :type manipulator_id: str
        :return: Callback as :class:`ephys_link.common.PositionalOutputData`
        :rtype: str
        """
        # com.dprint(f"[EVENT]\t\t Get position of manipulator" f" {manipulator_id}")

        return self.platform.get_pos(manipulator_id).json()

    async def get_angles(self, _, manipulator_id: str):
        """Angles of manipulator request

        :param _: Socket session ID (unused)
        :type _: str
        :param manipulator_id: ID of manipulator to pull angles from
        :type manipulator_id: str
        :return: Callback as :class:`ephys_link.common.AngularOutputData`
        :rtype: str
        """

        return self.platform.get_angles(manipulator_id).json()

    async def get_shank_count(self, _, manipulator_id: str) -> str:
        """Number of shanks of manipulator request

        :param _: Socket session ID (unused)
        :type _: str
        :param manipulator_id: ID of manipulator to pull number of shanks from
        :type manipulator_id: str
        :return: Callback as :class:`ephys_link.common.ShankCountOutputData`
        :rtype: str
        """

        return self.platform.get_shank_count(manipulator_id).json()

    async def goto_pos(self, _, data: com.GotoPositionInputDataFormat) -> str:
        """Move manipulator to position

        :param _: Socket session ID (unused)
        :type _: str
        :param data: Data containing manipulator ID, position in mm, and speed in mm/s
        :type data: :class:`ephys_link.common.GotoPositionInputDataFormat`
        :return: Callback as :class:`ephys_link.common.PositionalOutputData`
        :rtype: str
        """
        try:
            manipulator_id = data["manipulator_id"]
            pos = data["pos"]
            speed = data["speed"]
        except KeyError:
            manipulator_id = data["manipulator_id"] if "manipulator_id" in data else -1
            print(f"[ERROR]\t\t Invalid data for manipulator {manipulator_id}\n")
            return com.PositionalOutputData([], "Invalid data format").json()
        except Exception as e:
            print(f"[ERROR]\t\t Error in goto_pos: {e}\n")
            return com.PositionalOutputData([], "Error in goto_pos").json()
        else:
            com.dprint(f"[EVENT]\t\t Move manipulator {manipulator_id} " f"to position {pos}")
            goto_result = await self.platform.goto_pos(manipulator_id, pos, speed)
            return goto_result.json()

    async def drive_to_depth(self, _, data: com.DriveToDepthInputDataFormat) -> str:
        """Drive to depth

        :param _: Socket session ID (unused)
        :type _: str
        :param data: Data containing manipulator ID, depth in mm, and speed in mm/s
        :type data: :class:`ephys_link.common.DriveToDepthInputDataFormat`
        :return: Callback as :class:`ephys_link.common.DriveToDepthOutputData`
        :rtype: str
        """
        try:
            manipulator_id = data["manipulator_id"]
            depth = data["depth"]
            speed = data["speed"]
        except KeyError:
            manipulator_id = data["manipulator_id"] if "manipulator_id" in data else -1
            print(f"[ERROR]\t\t Invalid data for manipulator {manipulator_id}\n")
            return com.DriveToDepthOutputData(-1, "Invalid data " "format").json()
        except Exception as e:
            print(f"[ERROR]\t\t Error in drive_to_depth: {e}\n")
            return com.DriveToDepthOutputData(-1, "Error in drive_to_depth").json()
        else:
            com.dprint(f"[EVENT]\t\t Drive manipulator {manipulator_id} " f"to depth {depth}")
            drive_result = await self.platform.drive_to_depth(manipulator_id, depth, speed)
            return drive_result.json()

    async def set_inside_brain(self, _, data: com.InsideBrainInputDataFormat) -> str:
        """Set the inside brain state

        :param _: Socket session ID (unused)
        :type _: str
        :param data: Data containing manipulator ID and inside brain state
        :type data: :class:`ephys_link.common.InsideBrainInputDataFormat`
        :return: Callback as :class:`ephys_link.common.StateOutputData`:
        :rtype: str
        """
        try:
            manipulator_id = data["manipulator_id"]
            inside = data["inside"]
        except KeyError:
            manipulator_id = data["manipulator_id"] if "manipulator_id" in data else -1
            print(f"[ERROR]\t\t Invalid data for manipulator {manipulator_id}\n")
            return com.StateOutputData(False, "Invalid data format").json()
        except Exception as e:
            print(f"[ERROR]\t\t Error in inside_brain: {e}\n")
            return com.StateOutputData(False, "Error in set_inside_brain").json()
        else:
            com.dprint(f"[EVENT]\t\t Set manipulator {manipulator_id} inside brain to {"true" if inside else "false"}")
            return self.platform.set_inside_brain(manipulator_id, inside).json()

    async def calibrate(self, _, manipulator_id: str) -> str:
        """Calibrate manipulator

        :param _: Socket session ID (unused)
        :type _: str
        :param manipulator_id: ID of manipulator to calibrate
        :type manipulator_id: str
        :return: Error message (on error)
        :rtype: str
        """
        com.dprint(f"[EVENT]\t\t Calibrate manipulator" f" {manipulator_id}")

        return await self.platform.calibrate(manipulator_id, self.sio)

    async def bypass_calibration(self, _, manipulator_id: str) -> str:
        """Bypass calibration of manipulator

        :param _: Socket session ID (unused)
        :type _: str
        :param manipulator_id: ID of manipulator to bypass calibration
        :type manipulator_id: str
        :return: Error message (on error)
        :rtype: str
        """
        com.dprint(f"[EVENT]\t\t Bypass calibration of manipulator" f" {manipulator_id}")

        return self.platform.bypass_calibration(manipulator_id)

    async def set_can_write(self, _, data: com.CanWriteInputDataFormat) -> com.StateOutputData:
        """Set manipulator can_write state

        :param _: Socket session ID (unused)
        :type _: str
        :param data: Data containing manipulator ID and can_write brain state
        :type data: :class:`ephys_link.common.CanWriteInputDataFormat`
        :return: Callback as :class:`ephys_link.common.StateOutputData`
        :rtype: str
        """
        try:
            manipulator_id = data["manipulator_id"]
            can_write = data["can_write"]
            hours = data["hours"]

        except KeyError:
            manipulator_id = data["manipulator_id"] if "manipulator_id" in data else -1
            print(f"[ERROR]\t\t Invalid data for manipulator {manipulator_id}\n")
            return com.StateOutputData(False, "Invalid data " "format")

        except Exception as e:
            print(f"[ERROR]\t\t Error in inside_brain: {e}\n")
            return com.StateOutputData(False, "Error in set_can_write")
        else:
            com.dprint(
                f"[EVENT]\t\t Set manipulator {manipulator_id} can_write state to {"true" if can_write else "false"}"
            )
            return self.platform.set_can_write(manipulator_id, can_write, hours, self.sio)

    def stop(self, _) -> bool:
        """Stop all manipulators

        :param _: Socket session ID (unused)
        :type _: str
        :return: True if successful, False otherwise
        :rtype: bool
        """
        com.dprint("[EVENT]\t\t Stop all manipulators")

        return self.platform.stop()

    @staticmethod
    async def catch_all(_, __, data: Any) -> str:
        """Catch all event

        :param _: Socket session ID (unused)
        :type _: str
        :param __: Client ID (unused)
        :type __: str
        :param data: Data received from client
        :type data: Any
        :return: "UNKNOWN_EVENT" response message
        :rtype: str
        """
        print(f"[UNKNOWN EVENT]:\t {data}")
        return "UNKNOWN_EVENT"

    def launch_server(self, platform_type: str, server_port: int, pathfinder_port: int) -> None:
        """Launch the server

        :param platform_type: Parsed argument for platform type
        :type platform_type: str
        :param server_port: HTTP port to serve the server
        :type server_port: int
        :param pathfinder_port: Port New Scale Pathfinder's server is on
        :type pathfinder_port: int
        :return: None
        """

        # Import correct manipulator handler
        if platform_type == "sensapex":
            self.platform = importlib.import_module("ephys_link.platforms.sensapex_handler").SensapexHandler()
        elif platform_type == "ump3":
            self.platform = importlib.import_module("ephys_link.platforms.ump3_handler").UMP3Handler()
        elif platform_type == "new_scale":
            self.platform = importlib.import_module("ephys_link.platforms.new_scale_handler").NewScaleHandler()
        elif platform_type == "new_scale_pathfinder":
            self.platform = importlib.import_module(
                "ephys_link.platforms.new_scale_pathfinder_handler"
            ).NewScalePathfinderHandler(pathfinder_port)
        else:
            sys.exit(f"[ERROR]\t\t Invalid manipulator type: {platform_type}")

        # Preamble
        print(f"=== Ephys Link v{version} ===")

        # List available manipulators
        print("Available Manipulators:")
        print(self.platform.get_manipulators()["manipulators"])

        print("\n(Shutdown server with CTRL+Pause/Break)\n")

        # Mark that server is running
        self.is_running = True
        web.run_app(self.app, port=server_port)

    def close_server(self, _, __) -> None:
        """Close the server"""
        print("[INFO]\t\t Closing server")

        # Stop movement
        self.platform.stop()

        # Exit
        raise GracefulExit
