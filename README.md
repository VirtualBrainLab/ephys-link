# Electrophysiology Manipulator Link

[![PyPI version](https://badge.fury.io/py/ephys-link.svg)](https://badge.fury.io/py/ephys-link)
[![CodeQL](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/codeql-analysis.yml)
[![Dependency Review](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/dependency-review.yml/badge.svg)](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/dependency-review.yml)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

<!-- [![Build](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/build.yml/badge.svg)](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/build.yml) -->

The [Electrophysiology Manipulator Link](https://github.com/VirtualBrainLab/ephys-link)
(or Ephys Link for short) is a Python [Socket.IO](https://socket.io/docs/v4/#what-socketio-is) server that allows any
Socket.IO-compliant application (such
as [Pinpoint](https://github.com/VirtualBrainLab/Pinpoint))
to communicate with manipulators used in electrophysiology experiments.

<img width="100%" src="https://github.com/VirtualBrainLab/ephys-link/assets/82800265/0c7c60b1-0926-4697-a461-221554f82de1" alt="Manipulator and probe in pinpoint moving in sync">

**Supported Manipulators:**

| Manufacturer | Model                                                   |
|--------------|---------------------------------------------------------|
| Sensapex     | <ul> <li>uMp-4</li> <li>uMp-3 (Coming Soon!)</li> </ul> |
| New Scale    | <ul> <li>Pathfinder MPM Control v2.8+</li> </ul>        |
| Scientifica  | <ul> <li>InVivoStar (Coming Soon!)</li> </ul>           |
| LabMaker     | <ul> <li>(Coming Soon!)</li> </ul>                      |

Ephys Link is an open and extensible platform. It is designed to easily support integration with other manipulators.

For more information regarding the server's implementation and how the code is organized, see
the [package's development documentation](https://virtualbrainlab.org/ephys_link/development.html).

For detailed descriptions of the server's API, see
the [API reference](https://virtualbrainlab.org/api_reference_ephys_link.html).

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

# Documentation and More Information

Complete documentation including API usage and development installation can be
found on the [Virtual Brain Lab Documentation page][docs] for Ephys Link.

# Citing

If this project is used as part of a research project you should cite
the [Pinpoint repository][Pinpoint]. Please email
Dan ([dbirman@uw.edu](mailto:dbirman@uw.edu)) if you have questions.

Please reach out to Kenneth ([kjy5@uw.edu](mailto:kjy5@uw.edu)) for questions
about the Electrophysiology Manipulator Link server. Bugs may be reported
through the issues tab.

[Pinpoint]: https://github.com/VirtualBrainLab/Pinpoint

[StopSignal]: https://github.com/VirtualBrainLab/StopSignal

[docs]: https://virtualbrainlab.org/ephys_link/installation_and_use.html
