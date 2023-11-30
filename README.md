# Electrophysiology Manipulator Link

[![PyPI version](https://badge.fury.io/py/ephys-link.svg)](https://badge.fury.io/py/ephys-link)
[![CodeQL](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/codeql-analysis.yml)
[![Dependency Review](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/dependency-review.yml/badge.svg)](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/dependency-review.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

 <img width="100%" src="https://github.com/VirtualBrainLab/ephys-link/assets/82800265/c89e433c-2ce0-4f27-aa9d-66f89c59c979" alt="Manipulator and probe in pinpoint moving in sync">

The [Electrophysiology Manipulator Link](https://github.com/VirtualBrainLab/ephys-link)
(or Ephys Link for short) is a Python [Socket.IO](https://socket.io/docs/v4/#what-socketio-is) server that allows any
Socket.IO-compliant application (such
as [Pinpoint](https://github.com/VirtualBrainLab/Pinpoint))
to communicate with manipulators used in electrophysiology experiments.

Currently, Ephys Link only supports Sensapex uMp-4 Micromanipulators and New Scale 3-axis
manipulators. However, this platform is designed to be extensible to other
manipulators and more may be added in the future.

For more information regarding the server's implementation and how the code is organized, see
the [package's development documentation](https://virtualbrainlab.org/ephys_link/development.html).

For detailed descriptions of the server's API, see
the [API reference](https://virtualbrainlab.org/api_reference_ephys_link.html).

# Installation

## Prerequisites

1. [Python ≥ 3.8, < 3.13](https://www.python.org/downloads/release/python-3116/)
    1. Python 3.12+ requires the latest version
       of [Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (MSVC v143+) to
       be installed.
2. An **x86 Windows PC is required** to run the server.
3. For Sensapex devices, the controller unit must be connected via an ethernet
   cable and powered. A USB-to-ethernet adapter is acceptable. For New Scale manipulators,
   the controller unit must be connected via USB and be powered by a 6V power
   supply.
4. To use the emergency stop feature, ensure an Arduino with
   the [StopSignal](https://github.com/VirtualBrainLab/StopSignal) sketch is
   connected to the computer. Follow the instructions on that repo for how to
   set up the Arduino.

> ### Using a Python virtual environment is encouraged.
>
> Create a virtual environment by running `python -m venv ephys_link`
>
> Activate the environment by running `.\ephys_link\scripts\activate`
>
> A virtual environment helps to isolate installed packages from other packages on your computer and ensures a clean
> installation of Ephys Link

**NOTE:** Ephys Link is an HTTP server without cross-origin support. The server
is currently designed to interface with local/desktop instances of Pinpoint. It
will not work with the web browser versions of Pinpoint at this time.

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
2. Run the following command in the root directory of the repository to install the package along with development
   tools:

   ```bash
   pip install -e .[dev]
   ```

# Usage

Run the following commands in a terminal to start the server for the desired manipulator platform:

| Manipulator Platform                 | Command                              |
|--------------------------------------|--------------------------------------|
| Sensapex UMP-4                       | `ephys-link`                         |
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
