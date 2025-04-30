"""Globally accessible constants"""

from os.path import abspath, dirname, join

from vbl_aquarium.models.ephys_link import SetPositionRequest
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
    'Can not move manipulator while inside the brain. Set the depth ("set_depth") instead.'
)


def did_not_reach_target_position_error(request: SetPositionRequest, axis_index: int, final_position: Vector4) -> str:
    """Generate an error message for when the manipulator did not reach the target position.
    Args:
        request: The SetPositionRequest object containing the requested position.
        axis_index: The index of the axis that did not reach the target position.
        final_position: The final position of the manipulator.
    Returns:
        str: The error message.
    """
    return f"Manipulator {request.manipulator_id} did not reach target position on axis {list(Vector4.model_fields.keys())[axis_index]}. Requested: {request.position}, got: {final_position}"
