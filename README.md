# Electrophysiology Manipulator Link

The Electrophysiology Manipulator Link (or Ephys Link for short) is a Python WebSocket server that allows any
WebSocket-compliant application
(such as [Pinpoint (Neuropixels Trajectory Planner)](https://github.com/dbirman/NPTrajectoryPlanner/)) to
communication with manipulators used in electrophysiology experiments.

Currently, Ephys Link only supports Sensapex uMp Micromanipulators. However, this platform is designed to be extensible
to other manipulators and more may be added in the future.

# Installation

An x86 machine is required to run this server. Running the server on Windows to control Sensapex devices is
recommended and has been verified to work with the server. Communication with Sensapex devices is unverified for Linux
and macOS, however, development of the server is possible on a Linux operating system (Mac users should use Docker).

1. Ensure Python 3.8+ and pip are installed
2. `pip install ephys-link`
3. Run `python -m ephys-link` to start the server
    1. To view available command-line arguments, run `python -m ephys-link --help`
    2. Note: all arguments are optional and none are needed to use the server normally

# Usage and more

Complete documentation including API usage and development installation can be found on
the [Virtual Brain Lab Documentation page](https://virtualbrainlab.org/05_misc/03_ephys_link.html)
for this server

# Citing

If this project is used as part of a research project you should cite
the [Pinpoint repository](https://github.com/VirtualBrainLab/NPTrajectoryPlanner). Please email
Dan ([dbirman@uw.edu](mailto:dbirman@uw.edu)) if
you have questions.

Please reach out to Kenneth ([kjy5@uw.edu](mailto:kjy5@uw.edu)) for questions about the Electrophysiology Manipulator
Link server. Bugs may be
reported through the issues tab.
