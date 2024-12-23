# Installation

## Prerequisites

1. An **x86 Windows PC is required** to run the server.
2. For Sensapex devices, the controller unit must be connected via an ethernet
   cable and powered. A USB-to-ethernet adapter is acceptable. For New Scale manipulators,
   the controller unit must be connected via USB and be powered by a 6V power
   supply.
3. To use the emergency stop feature, ensure an Arduino with
   the [StopSignal](https://github.com/VirtualBrainLab/StopSignal) sketch is
   connected to the computer. Follow the instructions on that repo for how to
   set up the Arduino.

## Launch from Pinpoint (Recommended)

Pinpoint comes bundled with the correct version of Ephys Link. If you are using Pinpoint on the same computer your
manipulators are connected to, you can launch the server from within Pinpoint. Follow the instructions in
the [Pinpoint documentation](https://virtualbrainlab.org/pinpoint/tutorials/tutorial_ephys_link.html#configure-and-launch-ephys-link).

## Install as Standalone Executable

1. Download the latest executable from
   the [releases page](https://github.com/VirtualBrainLab/ephys-link/releases/latest).
2. Double-click the executable file to launch the configuration window.
    1. Take note of the IP address and port. **Copy this information into Pinpoint to connect**.
3. Select the desired configuration and click "Launch Server".

The configuration window will close and the server will launch. Your configurations will be saved for future use.

To connect to the server from Pinpoint, provide the IP address and port. For example, if the server is running on the
same computer that Pinpoint is, use

- Server: `localhost`
- Port: `8081`

If the server is running on a different (local) computer, use the IP address of that computer as shown in the startup
window instead of `localhost`.

## Install as a Python package

```bash
pip install ephys-link
```

Import main and run (this will launch the setup GUI).

```python
from ephys_link.__main__ import main

main()
```

## Install for Development

1. Clone the repository.
2. Install [Hatch](https://hatch.pypa.io/latest/install/)
3. In a terminal, navigate to the repository's root directory and run

   ```bash
   hatch shell
   ```

This will create a virtual environment, install Python 12 (if not found), and install the package in editable mode.

If you encounter any dependency issues (particularly with `aiohttp`), try installing the latest Microsoft Visual C++
(MSVC v143+ x86/64) and the Windows SDK (10/11)
via [Visual Studio Build Tools Installer](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
