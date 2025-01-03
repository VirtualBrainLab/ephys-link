"""Graphical User Interface for Ephys Link.

Usage:
    Create a GUI instance and call `get_options()` to get the options.

    ```python
    GUI().get_options()
    ```
"""

from json import load
from os import makedirs
from os.path import exists, join
from socket import gethostbyname, gethostname
from sys import exit
from tkinter import CENTER, RIGHT, BooleanVar, E, IntVar, StringVar, Tk, ttk

from platformdirs import user_config_dir
from vbl_aquarium.models.ephys_link import EphysLinkOptions

from ephys_link.__about__ import __version__ as version

# Define options path.
OPTIONS_DIR = join(user_config_dir(), "VBL", "Ephys Link")
OPTIONS_FILENAME = "options.json"
OPTIONS_PATH = join(OPTIONS_DIR, OPTIONS_FILENAME)


class GUI:
    """Graphical User Interface for Ephys Link.

    Gathers options from the user and saves them to a file.
    """

    def __init__(self) -> None:
        """Setup GUI properties."""

        self._root = Tk()

        # Create default options.
        options = EphysLinkOptions()

        # Read options.
        if exists(OPTIONS_PATH):
            with open(OPTIONS_PATH) as options_file:
                options = EphysLinkOptions(**load(options_file))

        # Load options into GUI variables.
        self._ignore_updates = BooleanVar(value=options.ignore_updates)
        self._type = StringVar(value=options.type)
        self._debug = BooleanVar(value=options.debug)
        self._use_proxy = BooleanVar(value=options.use_proxy)
        self._proxy_address = StringVar(value=options.proxy_address)
        self._mpm_port = IntVar(value=options.mpm_port)
        self._serial = StringVar(value=options.serial)

        # Submit flag.
        self._submit = False

    def get_options(self) -> EphysLinkOptions:
        """Get options from GUI.

        Returns:
            Options gathered from the GUI.
        """

        # Launch GUI.
        self._build_gui()
        self._root.mainloop()

        # Exit if the user did not submit options.
        if not self._submit:
            exit(1)

        # Extract options from GUI.
        options = EphysLinkOptions(
            ignore_updates=self._ignore_updates.get(),
            type=self._type.get(),
            debug=self._debug.get(),
            use_proxy=self._use_proxy.get(),
            proxy_address=self._proxy_address.get(),
            mpm_port=self._mpm_port.get(),
            serial=self._serial.get(),
        )

        # Save options.
        makedirs(OPTIONS_DIR, exist_ok=True)
        with open(OPTIONS_PATH, "w+") as options_file:
            options_file.write(options.model_dump_json())

        # Return options
        return options

    def _build_gui(self) -> None:
        """Build GUI."""

        self._root.title(f"Ephys Link v{version}")

        mainframe = ttk.Frame(self._root, padding=3)
        mainframe.grid(column=0, row=0, sticky="news")
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        # Server serving settings.

        server_serving_settings = ttk.LabelFrame(mainframe, text="Serving Settings", padding=3)
        server_serving_settings.grid(column=0, row=0, sticky="news")

        # Local IP.
        ttk.Label(server_serving_settings, text="Local IP:", anchor=E, justify=RIGHT).grid(column=0, row=0, sticky="we")
        ttk.Label(server_serving_settings, text=gethostbyname(gethostname())).grid(column=1, row=0, sticky="we")

        # Proxy.
        ttk.Label(server_serving_settings, text="Use Proxy:", anchor=E, justify=RIGHT).grid(
            column=0, row=1, sticky="we"
        )
        ttk.Checkbutton(
            server_serving_settings,
            variable=self._use_proxy,
        ).grid(column=1, row=1, sticky="we")

        # Proxy address.
        ttk.Label(server_serving_settings, text="Proxy Address:", anchor=E, justify=RIGHT).grid(
            column=0, row=2, sticky="we"
        )
        ttk.Entry(server_serving_settings, textvariable=self._proxy_address, justify=CENTER).grid(
            column=1, row=2, sticky="we"
        )

        # Ignore updates.
        ttk.Label(server_serving_settings, text="Ignore Updates:", anchor=E, justify=RIGHT).grid(
            column=0, row=4, sticky="we"
        )
        ttk.Checkbutton(
            server_serving_settings,
            variable=self._ignore_updates,
        ).grid(column=1, row=4, sticky="we")

        # Debug mode.
        ttk.Label(server_serving_settings, text="Debug mode:", anchor=E, justify=RIGHT).grid(
            column=0, row=5, sticky="we"
        )
        ttk.Checkbutton(
            server_serving_settings,
            variable=self._debug,
        ).grid(column=1, row=5, sticky="we")

        # ---

        # Platform type.
        platform_type_settings = ttk.LabelFrame(mainframe, text="Platform Type", padding=3)
        platform_type_settings.grid(column=0, row=1, sticky="news")

        ttk.Radiobutton(
            platform_type_settings,
            text="Sensapex uMp-4",
            variable=self._type,
            value="ump-4",
        ).grid(column=0, row=0, sticky="we")
        ttk.Radiobutton(
            platform_type_settings,
            text="Sensapex uMp-3",
            variable=self._type,
            value="ump-3",
        ).grid(column=0, row=1, sticky="we")
        ttk.Radiobutton(
            platform_type_settings,
            text="Pathfinder MPM Control v2.8.8+",
            variable=self._type,
            value="pathfinder-mpm",
        ).grid(column=0, row=2, sticky="we")
        ttk.Radiobutton(
            platform_type_settings,
            text="New Scale M3-USB-3:1-EP",
            variable=self._type,
            value="new-scale",
        ).grid(column=0, row=3, sticky="we")
        ttk.Radiobutton(
            platform_type_settings,
            text="Fake Platform",
            variable=self._type,
            value="fake",
        ).grid(column=0, row=4, sticky="we")

        # ---

        # New Scale Settings.
        new_scale_settings = ttk.LabelFrame(mainframe, text="Pathfinder MPM Settings", padding=3)
        new_scale_settings.grid(column=0, row=2, sticky="news")

        # Port
        ttk.Label(new_scale_settings, text="HTTP Server Port:", anchor=E, justify=RIGHT).grid(
            column=0, row=1, sticky="we"
        )
        ttk.Entry(new_scale_settings, textvariable=self._mpm_port, width=5, justify=CENTER).grid(
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
            command=self._launch_server,
        ).grid(column=0, row=4, columnspan=2, sticky="we")

    def _launch_server(self) -> None:
        """Close GUI and return to the server.

        Options are saved in fields.
        """
        self._submit = True
        self._root.destroy()
