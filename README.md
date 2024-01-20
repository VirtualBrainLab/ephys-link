# Electrophysiology Manipulator Link

[![PyPI version](https://badge.fury.io/py/ephys-link.svg)](https://badge.fury.io/py/ephys-link)
[![CodeQL](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/codeql-analysis.yml)
[![Dependency Review](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/dependency-review.yml/badge.svg)](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/dependency-review.yml)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

<img width="100%" src="https://github.com/VirtualBrainLab/ephys-link/assets/82800265/0c7c60b1-0926-4697-a461-221554f82de1" alt="Manipulator and probe in pinpoint moving in sync">

The [Electrophysiology Manipulator Link](https://github.com/VirtualBrainLab/ephys-link)
(or Ephys Link for short) is a Python [Socket.IO](https://socket.io/docs/v4/#what-socketio-is) server that allows any
Socket.IO-compliant application (such
as [Pinpoint](https://github.com/VirtualBrainLab/Pinpoint))
to communicate with manipulators used in electrophysiology experiments.

**Supported Manipulators:**

| Manufacturer | Model                                                                     |
|--------------|---------------------------------------------------------------------------|
| Sensapex     | <ul> <li>uMp-4</li> <li>uMp-3</li> </ul>                                  |
| New Scale    | <ul> <li>Pathfinder MPM Control v2.8.8+</li> <li>M3-USB-3:1-EP</li> </ul> |

Ephys Link is an open and extensible platform. It is designed to easily support integration with other manipulators.

For more information regarding the server's implementation and how the code is organized, see
the [package's development documentation](https://virtualbrainlab.org/ephys_link/development.html).

For detailed descriptions of the server's API, see
the [API reference](https://virtualbrainlab.org/api_reference_ephys_link.html).

# Installation

## Prerequisites

1. [Python ≥ 3.8, < 3.13](https://www.python.org/downloads/release/python-3116/)
    1. Python 3.12+ requires the latest version
       of Microsoft Visual C++ (MSVC v143+ x86/64) and the Windows SDK (10/11) to
       be installed. They can be acquired through
       the [Visual Studio Build Tools Installer](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
2. An **x86 Windows PC is required** to run the server.
3. For Sensapex devices, the controller unit must be connected via an ethernet
   cable and powered. A USB-to-ethernet adapter is acceptable. For New Scale manipulators,
   the controller unit must be connected via USB and be powered by a 6V power
   supply.
4. To use the emergency stop feature, ensure an Arduino with
   the [StopSignal](https://github.com/VirtualBrainLab/StopSignal) sketch is
   connected to the computer. Follow the instructions on that repo for how to
   set up the Arduino.

**NOTE:** Ephys Link is an HTTP server without cross-origin support. The server
is currently designed to interface with local/desktop instances of Pinpoint. It
will not work with the web browser versions of Pinpoint at this time.

<div style="padding: 15px; border: 1px solid transparent; border-color: transparent; margin-bottom: 20px; border-radius: 4px; color: #31708f; background-color: #d9edf7; border-color: #bce8f1;">
<h3>Using a Python virtual environment is encouraged.</h3>
<p>Create a virtual environment by running <code>python -m venv ephys_link</code></p>
<p>Activate the environment by running <code>.\ephys_link\scripts\activate</code></p>
<p>A virtual environment helps to isolate installed packages from other packages on your computer and ensures a clean installation of Ephys Link</p>
</div>

## Install for use

Run the following command to install the server:

```bash
pip install ephys-link
```

Update the server like any other Python package:

```bash
pip install --upgrade ephys-link
```

## Install for development

1. Clone the repository.
2. Install [Hatch](https://hatch.pypa.io/latest/install/)
3. In a terminal, navigate to the repository's root directory and run

   ```bash
   hatch shell
   ```

This will create a virtual environment and install the package in editable mode.

# Usage

Run the following commands in a terminal to start the server for the desired manipulator platform:

| Manipulator Platform                 | Command                              |
|--------------------------------------|--------------------------------------|
| Sensapex uMp-4                       | `ephys-link`                         |
| Sensapex uMp-3                       | `ephys-link -t ump3`                 |
| New Scale                            | `ephys-link -t new_scale`            |
| New Scale via Pathfinder HTTP server | `ephys-link -t new_scale_pathfinder` |

There are a couple additional aliases for the Ephys Link executable: `ephys_link` and `el`.

By default, the server will broadcast with its local IP address on port 8081.
**Copy this information into Pinpoint to connect**.

For example, if the server is running on the same computer that Pinpoint is, use

- Server: `localhost`
- Port: `8081`

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
