from argparse import ArgumentParser
from signal import SIGINT, SIGTERM, signal

from ephys_link import common as com
from ephys_link.__about__ import __version__ as version
from ephys_link.emergency_stop import EmergencyStop
from ephys_link.gui import GUI
from ephys_link.server import Server

# Setup argument parser.
parser = ArgumentParser(
    description="Electrophysiology Manipulator Link: a websocket interface for"
    " manipulators in electrophysiology experiments",
    prog="python -m ephys-link",
)
parser.add_argument(
    "-b", "--background", dest="background", action="store_true", help="Launches in headless mode (no GUI)"
)
parser.add_argument(
    "-t",
    "--type",
    type=str,
    dest="type",
    default="sensapex",
    help='Manipulator type (i.e. "sensapex", "new_scale", or "new_scale_pathfinder").' ' Default: "sensapex"',
)
parser.add_argument("-d", "--debug", dest="debug", action="store_true", help="Enable debug mode")
parser.add_argument(
    "-p",
    "--port",
    type=int,
    default=8081,
    dest="port",
    help="Port to serve on. Default: 8081 (avoids conflict with other HTTP servers)",
)
parser.add_argument(
    "--pathfinder_port",
    type=int,
    default=8080,
    dest="pathfinder_port",
    help="Port New Scale Pathfinder's server is on. Default: 8080",
)
parser.add_argument(
    "-s",
    "--serial",
    type=str,
    default="no-e-stop",
    dest="serial",
    nargs="?",
    help="Emergency stop serial port (i.e. COM3). Default: disables emergency stop",
)
parser.add_argument(
    "-v",
    "--version",
    action="version",
    version=f"Electrophysiology Manipulator Link v{version}",
    help="Print version and exit",
)


def main() -> None:
    """Main function"""

    # Parse arguments.
    args = parser.parse_args()

    # Launch GUI if not background.
    if not args.background:
        gui = GUI()
        gui.launch()
        return None

    # Otherwise, create Server from CLI.
    server = Server()

    # Continue with CLI if not.
    com.DEBUG = args.debug

    # Setup serial port.
    if args.serial != "no-e-stop":
        e_stop = EmergencyStop(server, args.serial)
        e_stop.watch()

    # Register server exit.
    signal(SIGTERM, server.close_server)
    signal(SIGINT, server.close_server)

    # Launch with parsed arguments on main thread.
    server.launch_server(args.type, args.port, args.pathfinder_port)


if __name__ == "__main__":
    main()
