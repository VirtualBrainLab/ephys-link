# Electrophysiology Manipulator Link

The Electrophysiology Manipulator Link is a Python WebSocket server that allows any WebSocket-compliant application
(such as [Pinpoint (Neuropixels Trajectory Planner)](https://github.com/dbirman/NPTrajectoryPlanner/)) to
communication with manipulators used in electrophysiology experiments.

As of writing (August 2022), Electrophysiology Manipulator Link supports Sensapex uMp compatible micromanipulators.

# Installation

An x86 machine is required to run this server. Windows is recommended for smoothest compatibility with other manipulator
software, however, Linux and macOS are also supported.

1. Ensure Python 3.8+ and pip are installed
2. `pip install ephys-manip-link`
3. Run `python -m ephys-manip-link` to start the server
    1. To view available command-line arguments, run `python -m ephys-manip-link --help`
    2. Note: all arguments are optional and none are needed to use the server normally

# Usage and more

Complete documentation including API usage and development installation can be found on
the [Virtual Brain Lab Documentation page](https://virtualbrainlab.org/build/html/05_misc/03_ephys_manip_link.html)
for this server

# Citing

If this project is used as part of a research project you should cite
the [Pinpoint repository](https://github.com/VirtualBrainLab/NPTrajectoryPlanner). Please email Dan (dbirman@uw.edu) if
you have questions.

Please reach out to Kenneth (kjy5@uw.edu) for questions about the Electrophysiology Manipulator Link server. Bugs may be
reported through the issues tab.
