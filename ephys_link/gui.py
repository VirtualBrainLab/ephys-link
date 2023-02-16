# pylama:skip=1
import socket
from argparse import Namespace
from threading import Event, Thread
from tkinter import *
from tkinter import ttk

# GUI Variables
is_running = False
server_port: IntVar
platform_type: StringVar
new_scale_port: IntVar
e_stop_serial_port: StringVar
server_launch_button_text: StringVar


class GUI:
    """GUI definition for Ephys Link

    :param root: Root object of the Tk GUI
    :type root: Tk
    """

    def __init__(
        self,
        root: Tk,
        launch_func: callable,
        manipulator_stop_func: callable,
        poll_serial_func: callable,
        parsed_args: Namespace,
    ) -> None:
        """Setup and construction of the Tk GUI"""

        # Fields
        self._root = root
        self._launch_func = launch_func
        self._manipulator_stop_func = manipulator_stop_func
        self._poll_serial_func = poll_serial_func
        self._kill_serial_event = Event()
        self._parsed_args = parsed_args

        # Update GUI variables with defaults
        global server_port, platform_type, new_scale_port, e_stop_serial_port
        global server_launch_button_text
        server_port = IntVar(value=self._parsed_args.port)
        platform_type = StringVar(value=self._parsed_args.type)
        new_scale_port = IntVar(value=self._parsed_args.new_scale_port)
        e_stop_serial_port = StringVar(value=self._parsed_args.serial)
        server_launch_button_text = StringVar(value="Start Server")

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

        server_serving_settings = ttk.LabelFrame(
            mainframe, text="Serving settings", padding=3
        )
        server_serving_settings.grid(column=0, row=0, sticky="news")

        # IP
        ttk.Label(server_serving_settings, text="IP:", anchor=E, justify=RIGHT).grid(
            column=0, row=0, sticky="we"
        )
        ttk.Label(
            server_serving_settings, text=socket.gethostbyname(socket.gethostname())
        ).grid(column=1, row=0, sticky="we")

        # Port
        ttk.Label(server_serving_settings, text="Port:", anchor=E, justify=RIGHT).grid(
            column=0, row=1, sticky="we"
        )
        ttk.Entry(
            server_serving_settings, textvariable=server_port, width=5, justify=CENTER
        ).grid(column=1, row=1, sticky="we")

        # ---

        # Platform type
        platform_type_settings = ttk.LabelFrame(
            mainframe, text="Platform Type", padding=3
        )
        platform_type_settings.grid(column=0, row=1, sticky="news")

        ttk.Radiobutton(
            platform_type_settings,
            text="Sensapex uMp",
            variable=platform_type,
            value="sensapex",
        ).grid(column=0, row=0, sticky="we")
        ttk.Radiobutton(
            platform_type_settings,
            text="New Scale",
            variable=platform_type,
            value="new_scale",
        ).grid(column=0, row=1, sticky="we")

        # ---

        # New Scale Settings
        new_scale_settings = ttk.LabelFrame(
            mainframe, text="New Scale settings", padding=3
        )
        new_scale_settings.grid(column=0, row=2, sticky="news")

        # Port
        ttk.Label(
            new_scale_settings, text="HTTP Server Port:", anchor=E, justify=RIGHT
        ).grid(column=0, row=1, sticky="we")
        ttk.Entry(
            new_scale_settings, textvariable=new_scale_port, width=5, justify=CENTER
        ).grid(column=1, row=1, sticky="we")

        # ---

        # Emergency Stop serial port
        e_stop_settings = ttk.LabelFrame(
            mainframe, text="Emergency Stop Settings", padding=3
        )
        e_stop_settings.grid(column=0, row=3, sticky="news")

        # Serial Port
        ttk.Label(e_stop_settings, text="Serial Port:", anchor=E, justify=RIGHT).grid(
            column=0, row=1, sticky="we"
        )
        ttk.Entry(
            e_stop_settings, textvariable=e_stop_serial_port, justify=CENTER
        ).grid(column=1, row=1, sticky="we")

        # Server start/stop button
        ttk.Button(
            mainframe,
            textvariable=server_launch_button_text,
            command=lambda: self.start_stop_server(not is_running),
        ).grid(column=0, row=4, columnspan=2, sticky="we")

    def start_stop_server(self, start: bool) -> None:
        """Start/stop server and update button text

        :param start: Whether to start or stop the server
        :type start: bool
        :return None
        """
        global server_port, server_launch_button_text, is_running
        is_running = not is_running
        if start:
            # Launch serial
            Thread(
                target=self._poll_serial_func,
                args=(
                    self._kill_serial_event,
                    e_stop_serial_port.get(),
                ),
                daemon=True,
            ).start()
            # Launch server
            Thread(
                target=self._launch_func,
                args=(platform_type.get(), server_port.get(), new_scale_port.get()),
                daemon=True,
            ).start()

            # Update UI
            server_launch_button_text.set("Close Server")
        else:
            # Stop serial
            self._kill_serial_event.set()

            # Stop manipulators
            self._manipulator_stop_func(0)

            # Close
            self._root.destroy()
