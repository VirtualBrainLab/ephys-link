import argparse
import signal
import time
from importlib import metadata
from threading import Event, Thread

import serial
import serial.tools.list_ports as ports

from ephys_link import common as com
from ephys_link.server import Server

# Setup Arduino serial port (emergency stop)
poll_rate = 0.05
kill_serial_event = Event()
poll_serial_thread: Thread

# Create Server
server = Server()


def poll_serial(kill_event: Event, serial_port: str) -> None:
    """Continuously poll serial port for data

    :param kill_event: Event to stop polling
    :type kill_event: Event
    :param serial_port: The serial port to poll
    :type serial_port: str
    :return: None
    """
    target_port = serial_port
    if serial_port is None:
        # Search for serial ports
        for port, desc, _ in ports.comports():
            if "Arduino" in desc or "USB Serial Device" in desc:
                target_port = port
                break
    elif serial_port == "no-e-stop":
        # Stop polling if no-e-stop is specified
        return None

    ser = serial.Serial(target_port, 9600, timeout=poll_rate)
    while not kill_event.is_set():
        if ser.in_waiting > 0:
            ser.readline()
            # Cause a break
            com.dprint("[EMERGENCY STOP]\t\t Stopping all manipulators")
            server.platform.stop()
            ser.reset_input_buffer()
        time.sleep(poll_rate)
    print("Close poll")
    ser.close()


def close_serial(_, __) -> None:
    """Close the serial connection"""
    print("[INFO]\t\t Closing serial")
    kill_serial_event.set()
    poll_serial_thread.join()


# Setup argument parser
parser = argparse.ArgumentParser(
    description="Electrophysiology Manipulator Link: a websocket interface for"
    " manipulators in electrophysiology experiments",
    prog="python -m ephys-link",
)
# parser.add_argument("-g", "--gui", dest="gui", action="store_true", help="Launches GUI")
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
    version=f"Electrophysiology Manipulator Link v{metadata.version('ephys_link')}",
    help="Print version and exit",
)


def main() -> None:
    """Main function"""

    # Parse arguments
    args = parser.parse_args()
    com.DEBUG = args.debug

    # Setup serial port
    if args.serial != "no-e-stop":
        # Register serial exit
        signal.signal(signal.SIGTERM, close_serial)
        signal.signal(signal.SIGINT, close_serial)

        # Start emergency stop system if serial is provided
        global poll_serial_thread
        poll_serial_thread = Thread(
            target=poll_serial,
            args=(
                kill_serial_event,
                args.serial,
            ),
            daemon=True,
        )
        poll_serial_thread.start()

    # Register server exit
    signal.signal(signal.SIGTERM, server.close_server)
    signal.signal(signal.SIGINT, server.close_server)

    # Launch with parsed arguments on main thread
    server.launch_server(args.type, args.port, args.pathfinder_port)


if __name__ == "__main__":
    main()
