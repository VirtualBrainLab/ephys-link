# Electrophysiology Manipulator Link

[![PyPI version](https://badge.fury.io/py/ephys-link.svg)](https://badge.fury.io/py/ephys-link)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)
[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)

<!-- [![Build](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/build.yml/badge.svg)](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/build.yml) -->

The [Electrophysiology Manipulator Link](https://github.com/VirtualBrainLab/ephys-link)
(or Ephys Link for short) is a Python [Socket.IO](https://socket.io/docs/v4/#what-socketio-is) server that allows any
Socket.IO-compliant application (such
as [Pinpoint][Pinpoint])
to communicate with manipulators used in electrophysiology experiments.

<img width="100%" src="https://github.com/VirtualBrainLab/ephys-link/assets/82800265/0c7c60b1-0926-4697-a461-221554f82de1" alt="Manipulator and probe in pinpoint moving in sync">

# Installation

## Pinpoint (Recommended)

Pinpoint comes bundled with the correct version of Ephys Link. If you are using Pinpoint on the same computer your
manipulators are connected to, you can launch the server from within Pinpoint. See the documentation
on [connecting from Pinpoint](../usage/using_ephys_link.md#connecting-to-pinpoint).

## Install as a Standalone Executable

Download the latest standalone executable or zip from
the [releases page](https://github.com/VirtualBrainLab/ephys-link/releases/latest).

Then see the [usage documentation](../usage/starting_ephys_link.md) for how to run the server.

# Documentation and More Information

Complete documentation including how to add manipulators and API usage can be
found on [Ephys Link's Documentation Website][docs].

# Citing

If this project is used as part of a research project you should cite
the [Pinpoint repository](https://github.com/VirtualBrainLab/Pinpoint). Please email
Dan ([dbirman@uw.edu](mailto:dbirman@uw.edu)) if you have questions.

Please reach out to Kenneth ([kjy5@uw.edu](mailto:kjy5@uw.edu)) for questions
about the Electrophysiology Manipulator Link server. Bugs may be reported
through the issues tab.

[Pinpoint]: https://github.com/VirtualBrainLab/Pinpoint

[docs]: https://ephys-link.virtualbrainlab.org
