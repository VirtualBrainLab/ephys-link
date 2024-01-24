from signal import SIGINT, SIGTERM, signal
from threading import Event, Thread
from time import sleep

from common import dprint
from serial import Serial
from serial.tools import list_ports
from server import Server


class EmergencyStop:
    """Serial system for emergency stop"""

    def __init__(self, server: Server, serial_port: str) -> None:
        """Setup serial port for emergency stop

        :param server: The Ephys Link server instance
        :type server: Server
        :param serial_port: The serial port to poll
        :type serial_port: str
        :return: None
        """
        self.server = server
        self.serial_port = serial_port
        self.poll_rate = 0.05
        self.kill_serial_event = Event()
        self.poll_serial_thread = Thread(target=self._poll_serial, daemon=True)

        # Register signals
        signal(SIGTERM, self._close_serial)
        signal(SIGINT, self._close_serial)

    def watch(self) -> None:
        """Start polling serial port for emergency stop"""
        self.poll_serial_thread.start()

    def _poll_serial(self) -> None:
        """Continuously poll serial port for data

        Close port on kill event
        """
        target_port = self.serial_port
        if self.serial_port is None:
            # Search for serial ports
            for port, desc, _ in list_ports.comports():
                if "Arduino" in desc or "USB Serial Device" in desc:
                    target_port = port
                    break

        serial = Serial(target_port, 9600, timeout=self.poll_rate)
        while not self.kill_serial_event.is_set():
            if serial.in_waiting > 0:
                serial.readline()
                # Cause a break
                dprint("[EMERGENCY STOP]\t\t Stopping all manipulators")
                self.server.platform.stop()
                serial.reset_input_buffer()
            sleep(self.poll_rate)
        print("Close poll")
        serial.close()

    def _close_serial(self, _, __) -> None:
        """Close the serial connection"""
        print("[INFO]\t\t Closing serial")
        self.kill_serial_event.set()
        self.poll_serial_thread.join()
