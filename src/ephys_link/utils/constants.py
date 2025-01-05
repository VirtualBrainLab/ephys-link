"""Globally accessible constants"""

from os.path import abspath, dirname, join

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
