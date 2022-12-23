from tkinter import *
from tkinter import ttk
from argparse import Namespace


class GUI:
    """GUI definition for Ephys Link

    :param root: Root object of the Tk GUI
    :type root: Tk
    """

    def __init__(self, root: Tk, launch_func: callable, close_func: callable,
                 stop_func: callable, parsed_args: Namespace) -> None:
        """Setup and construction of the Tk GUI"""

        # Fields
        self._root = root
        self._launch_func = launch_func
        self._close_func = close_func
        self._stop_func = stop_func
        self._parsed_args = parsed_args

        # Build GUI
        self.build_gui()

        # Launch server
        # self._launch_func(self._parsed_args.type, self._parsed_args.port,
        #                   self._parsed_args.serial, self._parsed_args.new_scale_port)

    def build_gui(self):
        """Build GUI"""

        self._root.title("Ephys Link")

        mainframe = ttk.Frame(self._root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky="news")
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)

        ttk.Label(mainframe, text="Ephys Link", font="TkHeadingFont").grid(column=0,
                                                                           row=0,
                                                                           sticky=W)
