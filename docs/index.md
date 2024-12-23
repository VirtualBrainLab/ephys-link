# Electrophysiology Manipulator Link

[![PyPI version](https://badge.fury.io/py/ephys-link.svg)](https://badge.fury.io/py/ephys-link)
[![CodeQL](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/codeql-analysis.yml)
[![Dependency Review](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/dependency-review.yml/badge.svg)](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/dependency-review.yml)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

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
