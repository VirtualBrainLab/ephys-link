# Installation

## Prerequisites

1. An **x86 Windows PC is required** to run the server.
2. For Sensapex devices, the controller unit must be connected via an ethernet
   cable and powered. A USB-to-ethernet adapter is acceptable. For New Scale manipulators,
   the controller unit must be connected via USB and be powered by a 6V power
   supply.
3. To use the emergency stop feature, ensure a keyboard is attached.

## Pinpoint (Recommended Method)

Pinpoint comes bundled with the correct version of Ephys Link. If you are using Pinpoint on the same computer your
manipulators are connected to, you can launch the server from within Pinpoint. See the documentation
on [connecting from Pinpoint](../usage/connecting_to_pinpoint.md).

## Install as a Standalone Executable

Download the latest standalone executable or zip from the [releases page](https://github.com/VirtualBrainLab/ephys-link/releases/latest).

Then see the [usage documentation](../usage/starting_ephys_link.md) for how to run the server.

## Install as a Python package

```bash
pip install ephys-link
```

or with [pipx](https://pipx.pypa.io/stable/) (recommended)

```bash
pipx install ephys-link
```

Then see the [usage documentation](../usage/starting_ephys_link.md) for how to run the server.

## Install for Development

See [development documentation](../development/index.md#installing-for-development) for more information.