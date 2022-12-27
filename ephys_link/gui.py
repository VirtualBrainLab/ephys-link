from tkinter import *
from tkinter import ttk
from argparse import Namespace
import socket
from threading import Thread, Event

# GUI Variables
is_running = False
server_port: IntVar
server_launch_button_text: StringVar


class GUI:
    """GUI definition for Ephys Link

    :param root: Root object of the Tk GUI
    :type root: Tk
    """

    def __init__(self, root: Tk, launch_func: callable,
                 manipulator_stop_func: callable, parsed_args: Namespace) -> None:
        """Setup and construction of the Tk GUI"""

        # Fields
        self._root = root
        self._launch_func = launch_func
        self._manipulator_stop_func = manipulator_stop_func
        self._parsed_args = parsed_args

        # Build GUI
        self.build_gui()

    def build_gui(self):
        """Build GUI"""

        self._root.title("Ephys Link")

        mainframe = ttk.Frame(self._root, padding=3)
        mainframe.grid(column=0, row=0, sticky="news")
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        # Server serving settings

        server_serving_settings = ttk.LabelFrame(mainframe, text="Serving settings",
                                                 padding=3)
        server_serving_settings.grid(column=0, row=0, sticky="news")

        # Setup segment variables
        global server_port, server_launch_button_text
        server_port = IntVar(server_serving_settings, value=self._parsed_args.port)
        server_launch_button_text = StringVar(server_serving_settings,
                                              value=f"Start on port "
                                                    f"{server_port.get()}")

        # IP
        ttk.Label(server_serving_settings, text="IP:", anchor=E, justify=RIGHT).grid(
            column=0, row=0, sticky="we")
        ttk.Label(server_serving_settings,
                  text=socket.gethostbyname(socket.gethostname())).grid(
            column=1,
            row=0,
            sticky="we")

        # Port
        ttk.Label(server_serving_settings, text="Port:", anchor=E, justify=RIGHT).grid(
            column=0, row=1, sticky="we")
        port_entry = ttk.Entry(server_serving_settings, textvariable=server_port,
                               width=5, justify=CENTER)
        port_entry.grid(column=1, row=1, sticky="we")

        # Server start/stop button
        ttk.Button(server_serving_settings,
                   textvariable=server_launch_button_text,
                   command=lambda: self.start_stop_server(not is_running)).grid(
            column=0,
            row=2,
            columnspan=2,
            sticky="we")

    def start_stop_server(self, start: bool) -> None:
        """Start/stop server and update button text

        :param start: Whether to start or stop the server
        :type start: bool
        :return None
        """
        global server_port, server_launch_button_text, is_running
        is_running = not is_running
        if start:
            # Launch server
            Thread(target=self._launch_func, args=(
                self._parsed_args.type, self._parsed_args.port,
                self._parsed_args.new_scale_port), daemon=True).start()

            # Update UI
            server_launch_button_text.set("Close Server")
        else:
            # Stop manipulators
            self._manipulator_stop_func(0)

            # Close
            self._root.destroy()
