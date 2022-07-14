# nptraj-sensapex-link

The Sensapex Link is a python WebSocket server that allows any WebSocket-compliant application (such
as [Pinpoint (Neuropixels Trajectory Planner)](https://github.com/dbirman/NPTrajectoryPlanner/)) to have limited
communication with [Sensapex uMp Micromanipulators](https://www.sensapex.com/products/ump-micromanipulators/)

# Installation

An x86 machine or Docker is required to install or run the server.

## Install locally and use like a standalone app/server

1. Ensure Python 3.8+ and pip are installed
2. `pip install nptraj-sensapex-link`
3. Run `python -m nptraj-sensapex-link` to start the server
    1. To view available command-line arguments, run `python -m nptraj-sensapex-link --help`
    2. Note: all arguments are optional and none are needed to use the server normally

## For usage like a library

1. Ensure Python 3.8+ and pip are installed
2. `pip install nptraj-sensapex-link`
3. Use `from nptraj_sensapex_link import launch` and call `launch()` to start the server
    1. Alternatively, use `import nptraj_sensapex_link` and call `nptraj_sensapex_link.launch()`

## To develop this package with a local install

1. Ensure Python 3.8+ and pip are installed
2. Clone the [repo](https://github.com/dbirman/nptraj-sensapex-link)
3. `cd nptraj-sensapex-link` and run `pip install -r requirements.txt`
4. The package is located in `src/`
5. `python src/nptraj_sensapex_link/server.py` launches the server
6. Unit tests are available to run under the `tests/` directory

## To develop this package with Docker

1. [Install Docker](https://www.docker.com/get-started/) in any way you like
2. Clone the [repo](https://github.com/dbirman/nptraj-sensapex-link)
3. `cd nptraj-sensapex-link`
4. `docker-compose up` to build the container
5. `docker attach <container-id>` to attach to the container
6. The package is located in `src/`
7. `python src/nptraj_sensapex_link/server.py` launches the server
8. Unit tests are available to run under the `tests/` directory
9. `docker-compose stop` to stop the container or `docker-compose down` to stop and remove the container

# Usage and more

Complete documentation can be found on
the [Virtual Brain Lab Documentation page](https://virtualbrainlab.org/build/html/02_traj_planner/04_sensapex_link.html)
for this server
