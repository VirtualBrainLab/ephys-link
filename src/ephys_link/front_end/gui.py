"""Graphical User Interface for Ephys Link.

Usage: create a GUI instance and call get_options() to get the options.
"""

from textual.app import App


class GUI(App):
    """Graphical User Interface for Ephys Link.

    Gathers options from the user and saves them to a file.
    """
