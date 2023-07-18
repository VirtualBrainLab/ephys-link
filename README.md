# Electrophysiology Manipulator Link

[![Autoformat and Lint](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/autoformat-and-lint.yml/badge.svg)](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/autoformat-and-lint.yml)
[![CodeQL](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/codeql-analysis.yml)
[![Dependency Review](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/dependency-review.yml/badge.svg)](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/dependency-review.yml)

The [Electrophysiology Manipulator Link](https://github.com/VirtualBrainLab/ephys-link)
(or Ephys Link for short) is a Python WebSocket server that allows any
WebSocket-compliant application (such
as [Pinpoint](https://github.com/VirtualBrainLab/Pinpoint))
to communicate with manipulators used in electrophysiology experiments.

Currently, Ephys Link only supports Sensapex uMp Micromanipulators and New Scale
manipulators. However, this platform is designed to be extensible to other
manipulators and more may be
added in the future.

For more information regarding the server's implementation and how the code is
organized, see
the [package's API reference](https://virtualbrainlab.org/api_reference_ephys_link.html)

## Installation

### Prerequisites

1. [Python 3.10+](https://www.python.org/downloads/) and pip.
2. An **x86 Windows PC is required** to run the server.
3. For Sensapex devices, the controller unit must be connected via an ethernet
   cable. A USB-to-ethernet adapter is acceptable. For New Scale manipulators,
   the controller unit must be connected via USB and be powered by a 6V power
   supply.
4. To use the emergency stop feature, ensure an Arduino with
   the [StopSignal](https://github.com/VirtualBrainLab/StopSignal) sketch is
   connected to the computer. Follow the instructions on that repo for how to
   set up the Arduino.

**NOTE:** Ephys Link is an HTTP server without cross-origin support. The server
is currently designed to interface with local/desktop instances of Pinpoint. It
will not work with the web browser versions of Pinpoint at this time.

### Install


>Using a Python virtual environment is encouraged.
>
>Create a virtual environment by running `python -m venv ephys_link`
>
>Activate the environment by running `.\ephys_link\scripts\activate`
>
>A virtual environment helps to isolate installed packages from other packages on your computer and ensures a clean installation of Ephys Link


Run the following command to install the server:

```bash
pip install ephys-link
```

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

[docs]: https://virtualbrainlab.org/ephys_link/installation_and_use.html
