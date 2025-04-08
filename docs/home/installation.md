# Installation

## Prerequisites

1. An **x86 Windows PC is required** to run the server.
2. For Sensapex devices, the controller unit must be powered and connected via an Ethernet
   cable to the computer running Ephys Link. A USB-to-Ethernet adapter is acceptable. For New Scale manipulators,
   the controller unit must be connected via USB and be powered by a 6V power
   supply.
3. To use the emergency stop feature, ensure a keyboard is attached.

## Pinpoint (recommended)

Pinpoint comes bundled with the correct version of Ephys Link. If you are using Pinpoint on the same computer your
manipulators are connected to, you can launch the server from within Pinpoint. See the documentation
on [connecting from Pinpoint](../usage/using_ephys_link.md#connecting-to-pinpoint).

## Install as a Standalone Executable

Download the latest standalone executable or zip from the [releases page](https://github.com/VirtualBrainLab/ephys-link/releases/latest).

Then see the [usage documentation](../usage/starting_ephys_link.md) for how to run the server.

## Install as a Python package (not reccomended)

Ephys Link is a Python package released on PyPI and can be included in projects as such.

**This is not the reccomended method of using Ephys Link.** This is only for advanced
use cases where Ephys Link is used as a library in another project. Ephys Link will exclusively support the latest version of Python its dependences support.

```bash
pip install ephys-link
```

Then see the [usage documentation](../usage/starting_ephys_link.md) for how to run the server.

## Install for Development

See [development documentation](../development/index.md#installing-for-development) for more information.
