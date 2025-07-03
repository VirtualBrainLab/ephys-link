"""Globally accessible constants"""

from os.path import abspath, dirname, join

from vbl_aquarium.models.ephys_link import SetDepthRequest, SetPositionRequest
from vbl_aquarium.models.unity import Vector4

# Ephys Link ASCII.
ASCII = r"""
 ______       _                 _      _       _
|  ____|     | |               | |    (_)     | |
| |__   _ __ | |__  _   _ ___  | |     _ _ __ | | __
|  __| | '_ \| '_ \| | | / __| | |    | | '_ \| |/ /
| |____| |_) | | | | |_| \__ \ | |____| | | | |   <
|______| .__/|_| |_|\__, |___/ |______|_|_| |_|_|\_\
       | |           __/ |
       |_|          |___/
"""

# Absolute path to the resource folder.
PACKAGE_DIRECTORY = dirname(dirname(abspath(__file__)))
RESOURCES_DIRECTORY = join(PACKAGE_DIRECTORY, "resources")
BINDINGS_DIRECTORY = join(PACKAGE_DIRECTORY, "bindings")

# Ephys Link Port
PORT = 3000

# Error messages

NO_SET_POSITION_WHILE_INSIDE_BRAIN_ERROR = (
    'Cannot move manipulator while inside the brain. Set the depth ("set_depth") instead.'
)


def did_not_reach_target_position_error(
    request: SetPositionRequest, axis_index: int, final_unified_position: Vector4
) -> str:
    """Generate an error message for when the manipulator did not reach the target position.
    Args:
        request: The object containing the requested position.
        axis_index: The index of the axis that did not reach the target position.
        final_unified_position: The final position of the manipulator.
    Returns:
        str: The error message.
    """
    return f"Manipulator {request.manipulator_id} did not reach target position on axis {list(Vector4.model_fields.keys())[axis_index]}. Requested: {request.position}, got: {final_unified_position}"


def did_not_reach_target_depth_error(request: SetDepthRequest, final_unified_depth: float) -> str:
    """Generate an error message for when the manipulator did not reach the target position.
    Args:
        request: The object containing the requested depth.
        final_unified_depth: The final depth of the manipulator.
    Returns:
        str: The error message.
    """
    return f"Manipulator {request.manipulator_id} did not reach target depth. Requested: {request.depth}, got: {final_unified_depth}"


EMERGENCY_STOP_MESSAGE = "Emergency Stopping All Manipulators..."

SERVER_NOT_INITIALIZED_ERROR = "Server not initialized."
PROXY_CLIENT_NOT_INITIALIZED_ERROR = "Proxy client not initialized."


def cannot_connect_as_client_is_already_connected_error(new_client_sid: str, current_client_sid: str) -> str:
    """Generate an error message for when the client is already connected.
    Args:
        new_client_sid: The SID of the new client.
        current_client_sid: The SID of the current client.
    Returns:
        str: The error message.
    """
    return f"Cannot connect {new_client_sid} as {current_client_sid} is already connected."


def client_disconnected_without_being_connected_error(client_sid: str) -> str:
    """Generate an error message for when the client is disconnected without being connected.
    Args:
        client_sid: The SID of the client.
    Returns:
        str: The error message.
    """
    return f"Client {client_sid} disconnected without being connected."


MALFORMED_REQUEST_ERROR = {"error": "Malformed request."}
UNKNOWN_EVENT_ERROR = {"error": "Unknown event."}

UNABLE_TO_CHECK_FOR_UPDATES_ERROR = (
    "Unable to check for updates. Ignore updates or use the the -i flag to disable checks.\n"
)


def ump_4_3_deprecation_error(cli_name: str):
    return f"CLI option '{cli_name}' is deprecated and will be removed in v3.0.0. Use 'ump' instead."


def unrecognized_platform_type_error(cli_name: str) -> str:
    """Generate an error message for when the platform type is not recognized.
    Args:
        cli_name: The platform type that is not recognized.
    Returns:
        str: The error message.
    """
    return f'Platform type "{cli_name}" not recognized.'
