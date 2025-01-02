# Developing with Ephys Link

Ephys Link is free and open-source software. All of our code is available
on [GitHub](https://github.com/VirtualBrainLab/ephys-link), and we welcome contributions from the community!

This section describes:

- [The Socket.IO server's API](socketio_api.md) and how to communicate with Ephys Link from a client application
- How to [add a new manipulator](adding_a_manipulator.md) to Ephys Link
- General [code organization](code_organization.md) and development practices for Ephys Link
- Auto generated [source code reference](../reference/SUMMARY.md) intended for developers who are maintaining Ephys Link

## Installing for Development

1. Clone the repository.
2. Install [Hatch](https://hatch.pypa.io/latest/install/)
3. In a terminal, navigate to the repository's root directory and run

   ```bash
   hatch shell
   ```

This will create a virtual environment, install Python 13 (if not found), and install the package in editable mode.

If you encounter any dependency issues (particularly with `aiohttp`), try installing the latest Microsoft Visual C++
(MSVC v143+ x86/64) and the Windows SDK (10/11)
via [Visual Studio Build Tools Installer](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
