# nptraj-sensapex-link
The Sensapex Link is a python server which allows any WebSocket compliant application (such as [Pinpoint (Neuropixels Trajectory Planner)](https://github.com/dbirman/NPTrajectoryPlanner/)) to have limited communication with [Sensapex uMp Micromanipulators](https://www.sensapex.com/products/ump-micromanipulators/)

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
3. `cd nptraj-sensapex-link` and run `pip install requirements.txt`
4. Get the [Sensapex uM SDK](http://dist.sensapex.com/misc/um-sdk/latest/) binary zip
   1. Currently (June 2022), the SDK version is that is compatible with the Sensapex python SDK is [v1.022](http://dist.sensapex.com/misc/um-sdk/latest/umsdk-1.022-binaries.zip)
   2. **Make sure the firmware version installed on the manipulators matches the SDK version you install**
5. Extract the zip and copy the DLL or lib file appropriate for your system into the installation location for the python Sensapex module
   1. i.e. if you are using a virtual environment in windows, copy the DLL into `{path to venv}/Lib/site-packages/sensapex/`
6. Upon completion, run `python main.py` to launch the server
7. Unit tests are available to run under the `tests/` directory
