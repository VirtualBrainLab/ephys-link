# Electrophysiology Manipulator Link

The Electrophysiology Manipulator Link (or Ephys Link for short) is a Python
WebSocket server that allows any WebSocket-compliant application (such
as [Pinpoint (electrophysiology planning tool)][Pinpoint])
to communication with manipulators used in electrophysiology experiments.

Currently, Ephys Link only supports Sensapex uMp Micromanipulators. However,
this platform is designed to be extensible to other manipulators and more may be
added in the future.

# Getting Started

## Prerequisites

1. A **x86 Windows PC is recommended** to run this server.
    1. The server has been verified to work well with Sensapex devices on
       Windows. This is unverified for Linux and
       macOS. However, developing the server is possible on a Linux operating
       system (macOS users should virtualize Linux).
2. For Sensapex devices, the controller unit must be connect to the PC via an Ethernet cable. A USB-to-Ethernet adapter is acceptable as well.
3. To use the emergency stop feature, ensure an Arduino with
   the [StopSignal][StopSignal] sketch is connected to the computer. Follow
   the instructions on that repo for how to set up the Arduino.

## Installation

1. Ensure Python 3.8+ and pip are installed
2. `pip install ephys-link`
3. Run `python -m ephys-link` to start the server
    1. To view available command-line arguments,
       run `python -m ephys-link --help`
    2. Note: all arguments are optional and none are needed to use the server
       normally

# Usage and more

Complete documentation including API usage and development installation can be
found on the [Virtual Brain Lab Documentation page][docs]for this server.

# Citing

If this project is used as part of a research project you should cite
the [Pinpoint repository][NPTrajectoryPlanner]. Please email
Dan ([dbirman@uw.edu](mailto:dbirman@uw.edu)) if you have questions.

Please reach out to Kenneth ([kjy5@uw.edu](mailto:kjy5@uw.edu)) for questions
about the Electrophysiology Manipulator Link server. Bugs may be reported
through the issues tab.

[Pinpoint]: https://github.com/VirtualBrainLab/Pinpoint

[StopSignal]: https://github.com/VirtualBrainLab/StopSignal

[docs]: https://virtualbrainlab.org/05_misc/03_ephys_link.html
