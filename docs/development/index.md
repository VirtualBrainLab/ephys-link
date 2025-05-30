# Developing with Ephys Link

Ephys Link is free and open-source software. All of our code is available
on [GitHub](https://github.com/VirtualBrainLab/ephys-link), and we welcome contributions from the community!

This section describes:

- [The Socket.IO server's API](socketio_api.md) and how to communicate with Ephys Link from a client application
- How to [add a new manipulator](adding_a_manipulator.md) to Ephys Link
- General [code organization](code_organization.md) for Ephys Link
- Auto-generated [source code reference](../reference/SUMMARY.md) intended for developers who are maintaining Ephys Link

## Installing for Development

1. Clone the repository.
2. Install [UV](https://docs.astral.sh/uv/#installation)
3. Install [Hatch](https://hatch.pypa.io/latest/install/)
4. In a terminal, navigate to the repository's root directory and run

   ```bash
   hatch shell
   ```

This will create a virtual environment, install the latest Python for this project (if not found), and install the
package in editable mode.

If you encounter any dependency issues (particularly with `aiohttp`), try installing the latest Microsoft Visual C++
(MSVC v143+ x86/64) and the Windows SDK (10/11)
via [Visual Studio Build Tools Installer](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

## Contributing Code

We recommend first time contributors to
read [this guide](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project) by
GitHub to understand how to contribute changes.

## Deploying New Releases

!!! note

    Only VBL members can make official releases.

There is a [GitHub action](https://github.com/VirtualBrainLab/ephys-link/actions/workflows/release.yml) configured to
build and publish Ephys Link as a standalone EXE and as a PyPI package. The trigger is to make and push a new tag.

```bash
git switch main
git tag v2.0.0
git push origin --tags
```