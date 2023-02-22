# Electrophysiology Manipulator Link

The Electrophysiology Manipulator Link (or Ephys Link for short) is a Python
WebSocket server that allows any WebSocket-compliant application (such
as [Pinpoint (electrophysiology planning tool)][Pinpoint])
to communicate with manipulators used in electrophysiology experiments.

Currently, Ephys Link only supports Sensapex uMp Micromanipulators. However,
this platform is designed to be extensible to other manipulators and more may be
added in the future.

# Getting Started

## Prerequisites

1. An **x86 Windows PC is recommended** to run this server.
    1. The server has been verified to work well with Sensapex devices on
       Windows. This is unverified for Linux and
       macOS. However, developing the server is possible on a Linux operating
       system (macOS users should virtualize Linux).
2. For Sensapex devices, the controller unit must be connected to the PC via an
   ethernet cable. A USB-to-ethernet adapter is acceptable as well.
3. To use the emergency stop feature, ensure an Arduino with
   the [StopSignal][StopSignal] sketch is connected to the computer. Follow
   the instructions on that repo for how to set up the Arduino.

**NOTE:** Ephys Link is an HTTP server without cross-origin support. The server is currently designed to interface with local/desktop instances of Pinpoint. It will not work with the web browser versions of Pinpoint at this time.

## Installation

1. Ensure Python 3.10+ and pip are installed
2. `pip install ephys-link --use-pep517`
    1. PEP 517 is needed to allow the Sensapex Manipulator API to be installed
3. Run `python -m ephys_link` to start the server
    1. To view available command-line arguments,
       run `python -m ephys_link --help`
    2. Note: all arguments are optional and none are needed to use the server
       normally

# Usage and more

Complete documentation including API usage and development installation can be
found on the [Virtual Brain Lab Documentation page][docs] for this server.

# Citing

If this project is used as part of a research project you should cite
the [Pinpoint repository][Pinpoint]. Please email
Dan ([dbirman@uw.edu](mailto:dbirman@uw.edu)) if you have questions.

Please reach out to Kenneth ([kjy5@uw.edu](mailto:kjy5@uw.edu)) for questions
about the Electrophysiology Manipulator Link server. Bugs may be reported
through the issues tab.

[Pinpoint]: https://github.com/VirtualBrainLab/Pinpoint

[StopSignal]: https://github.com/VirtualBrainLab/StopSignal

[docs]: https://virtualbrainlab.org/05_misc/03_ephys_link.html
