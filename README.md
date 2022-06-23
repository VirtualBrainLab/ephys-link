# nptraj-sensapex-link
The Sensapex Link is a python WebSocket server that allows any WebSocket compliant application (such as [Pinpoint (Neuropixels Trajectory Planner)](https://github.com/dbirman/NPTrajectoryPlanner/)) to have limited communication with [Sensapex uMp Micromanipulators](https://www.sensapex.com/products/ump-micromanipulators/)

# Installation
## For usage like a standalone app/server
1. Ensure Python 3.8+ and pip are installed
2. `pip install nptraj-sensapex-link`
3. Run `python -m nptraj-sensapex-link` to start the server

## For usage like a library
1. Ensure Python 3.8+ and pip are installed
2. `pip install nptraj-sensapex-link`
3. Use `from nptraj_sensapex_link import launch` and call `launch()` to start the server
   1. Alternatively, use `import nptraj_sensapex_link` and call `nptraj_sensapex_link.launch()`

## To develop this package
1. Ensure Python 3.8+ and pip are installed
2. Clone the [repo](https://github.com/dbirman/nptraj-sensapex-link)
3. `cd nptraj-sensapex-link` and run `pip install -r requirements.txt`
4. The package is located in `src/`
5. `python src/nptraj_sensapex_link/server.py` launches the server
6. Unit tests are available to run under the `tests/` directory

# Usage and more
Complete documentation can be found on the [Virtual Brain Lab Documentation page](https://virtualbrainlab.org/build/html/02_traj_planner/04_sensapex_link.html) for this server