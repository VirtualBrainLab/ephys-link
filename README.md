# Sensapex Link

The Sensapex Link is a python WebSocket server that allows any WebSocket-compliant application (such
as [Pinpoint (Neuropixels Trajectory Planner)](https://github.com/dbirman/NPTrajectoryPlanner/)) to have limited
communication with [Sensapex uMp Micromanipulators](https://www.sensapex.com/products/ump-micromanipulators/)

# Installation

An x86 machine is required to run this server. Windows is recommended for smoothest compatibility with other Sensapex software, however, Linux and macOS are also supported.

1. Ensure Python 3.8+ and pip are installed
2. `pip install nptraj-sensapex-link`
3. Run `python -m nptraj-sensapex-link` to start the server
    1. To view available command-line arguments, run `python -m nptraj-sensapex-link --help`
    2. Note: all arguments are optional and none are needed to use the server normally

# Usage and more

Complete documentation including API usage and development installation can be found on the [Virtual Brain Lab Documentation page](https://virtualbrainlab.org/build/html/05_misc/03_sensapex_link.html)
for this server


# Citing

If this project is used as part of a research project you should cite the [Pinpoint repository](https://github.com/VirtualBrainLab/NPTrajectoryPlanner). Please email Dan (dbirman@uw.edu) if you have questions.

Please reach out to Kenneth (kjy5@uw.edu) for questions about the Sensapex Link server. Bugs may be reported through the issues tab.
