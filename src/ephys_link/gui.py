import socket
from tkinter import CENTER, RIGHT, BooleanVar, E, IntVar, StringVar, Tk, ttk

import ephys_link.common as com
from ephys_link.__about__ import __version__ as version
from ephys_link.emergency_stop import EmergencyStop
from ephys_link.server import Server


class GUI:
    """GUI definition for Ephys Link"""

    def __init__(self) -> None:
        """Setup and construction of the Tk GUI"""

        self._root = Tk()

        self._type = StringVar(value="sensapex")
        self._debug = BooleanVar(value=False)
        self._port = IntVar(value=8081)
        self._pathfinder_port = IntVar(value=8080)
        self._serial = StringVar(value="no-e-stop")

    def launch(self) -> None:
        """Build and launch GUI"""

        # Build and run GUI.
        self._build_gui()
        self._root.mainloop()

        # Launch server based on GUI settings.
        server = Server()

        com.DEBUG = self._debug.get()

        if self._serial.get() != "no-e-stop":
            e_stop = EmergencyStop(server, self._serial.get())
            e_stop.watch()

        server.launch_server(self._type.get(), self._port.get(), self._pathfinder_port.get())

    def _build_gui(self):
        """Build GUI"""

        self._root.title(f"Ephys Link v{version}")

        mainframe = ttk.Frame(self._root, padding=3)
        mainframe.grid(column=0, row=0, sticky="news")
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        # Server serving settings.

        server_serving_settings = ttk.LabelFrame(mainframe, text="Serving settings", padding=3)
        server_serving_settings.grid(column=0, row=0, sticky="news")

        # IP.
        ttk.Label(server_serving_settings, text="IP:", anchor=E, justify=RIGHT).grid(column=0, row=0, sticky="we")
        ttk.Label(server_serving_settings, text=socket.gethostbyname(socket.gethostname())).grid(
            column=1, row=0, sticky="we"
        )

        # Port.
        ttk.Label(server_serving_settings, text="Port:", anchor=E, justify=RIGHT).grid(column=0, row=1, sticky="we")
        ttk.Entry(server_serving_settings, textvariable=self._port, width=5, justify=CENTER).grid(
            column=1, row=1, sticky="we"
        )

        # ---

        # Platform type.
        platform_type_settings = ttk.LabelFrame(mainframe, text="Platform Type", padding=3)
        platform_type_settings.grid(column=0, row=1, sticky="news")

        ttk.Radiobutton(
            platform_type_settings,
            text="Sensapex uMp",
            variable=self._type,
            value="sensapex",
        ).grid(column=0, row=0, sticky="we")
        ttk.Radiobutton(
            platform_type_settings,
            text="New Scale",
            variable=self._type,
            value="new_scale",
        ).grid(column=0, row=1, sticky="we")

        # ---

        # New Scale Settings.
        new_scale_settings = ttk.LabelFrame(mainframe, text="New Scale settings", padding=3)
        new_scale_settings.grid(column=0, row=2, sticky="news")

        # Port
        ttk.Label(new_scale_settings, text="HTTP Server Port:", anchor=E, justify=RIGHT).grid(
            column=0, row=1, sticky="we"
        )
        ttk.Entry(new_scale_settings, textvariable=self._pathfinder_port, width=5, justify=CENTER).grid(
            column=1, row=1, sticky="we"
        )

        # ---

        # Emergency Stop serial port.
        e_stop_settings = ttk.LabelFrame(mainframe, text="Emergency Stop Settings", padding=3)
        e_stop_settings.grid(column=0, row=3, sticky="news")

        # Serial Port
        ttk.Label(e_stop_settings, text="Serial Port:", anchor=E, justify=RIGHT).grid(column=0, row=1, sticky="we")
        ttk.Entry(e_stop_settings, textvariable=self._serial, justify=CENTER).grid(column=1, row=1, sticky="we")

        # Server launch button.
        ttk.Button(
            mainframe,
            text="Launch Server",
            command=lambda: self._root.destroy(),
        ).grid(column=0, row=4, columnspan=2, sticky="we")
