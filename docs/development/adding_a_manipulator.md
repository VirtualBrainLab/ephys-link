# Adding a Manipulator

By the end of this section, you will be able to add a manipulator platform to Ephys Link and control it using the server
API. This is a software development guide and assumes you have experience with Python. It is encouraged to
read [how the system works first](../home/how_it_works.md) before proceeding.

## Set Up for Development

1. Fork the [Ephys Link repository](https://github.com/VirtualBrainLab/ephys-link). If you're new to contributing, we
   recommend
   reading [this guide](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project)
   by GitHub.
2. Follow the instructions for [installing Ephys Link for development](index.md#installing-for-development) to get all
   the necessary dependencies and tools set up. In this case, you'll want to clone your fork.
3. (Optional) Familiarize yourself with the [repo's organization](code_organization.md).

## Create a Manipulator Binding

Manipulators are added to Ephys Link through bindings. A binding is a Python class that extends the abstract base class
[`BaseBinding`][ephys_link.utils.base_binding] and defines the methods Ephys Link expects from a platform.

Create a new Python module in `src/ephys_link/bindings` for your manipulator. Make a class that extends
[`BaseBinding`][ephys_link.utils.base_binding]. Most IDEs will automatically import the necessary classes and tell you
the methods you need to implement. See the reference for [`BaseBinding`][ephys_link.utils.base_binding] for detailed
descriptions of the expected behavior.

As described in the [system overview](../home/how_it_works.md), Ephys Link converts all manipulator movement into a
common "unified space" which is
the [left-hand cartesian coordinate system](https://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/geometry/coordinate-systems.html).
The two methods [
`platform_space_to_unified_space`](../reference/ephys_link/utils/base_binding.md#ephys_link.utils.base_binding.BaseBinding.platform_space_to_unified_space)
and [
`unified_space_to_platform_space`](../reference/ephys_link/utils/base_binding.md#ephys_link.utils.base_binding.BaseBinding.unified_space_to_platform_space)
are used to convert between your manipulator's coordinate system and the unified space.

!!! tip

    See
    the [Sensapex uMp-4](https://github.com/VirtualBrainLab/ephys-link/blob/main/src/ephys_link/bindings/ump_4_bindings.py)
    binding for an example where the platform has a Python API (Sensapex's SDK) and
    the [New Scale Pathfinder MPM](https://github.com/VirtualBrainLab/ephys-link/blob/main/src/ephys_link/bindings/mpm_bindings.py)
    binding, for example, where the platform uses a REST API for an external provider.

### Binding Names

The two naming methods [
`get_display_name`](../reference/ephys_link/utils/base_binding.md#ephys_link.utils.base_binding.BaseBinding.get_display_name)
and [
`get_cli_name`](../reference/ephys_link/utils/base_binding.md#ephys_link.utils.base_binding.BaseBinding.get_cli_name)
are used to identify the binding in the user interface. As described by their documentation, `get_display_name` should
return a human-readable name for the binding, while `get_cli_name` should return the name used to launch the binding
from the command line (what is passed to the `-t` flag). For example, Sensapex uMp-4 manipulator's `get_cli_name`
returns `ump-4` because the CLI launch command is `ephys_link.exe -b -t ump-4`.

### Custom Additional Arguments

Sometimes you may want to pass extra data to your binding on initialization. For example, New Scale Pathfinder MPM
bindings need to know what the HTTP server port is. To add custom arguments, define them as arguments on the `__init__`
method of your binding then pass in the appropriate data when the binding is instantiated in the [
`_get_binding_instance`](https://github.com/VirtualBrainLab/ephys-link/blob/f79c1ec68ec1805e1a4e231e1934127893f7bd20/src/ephys_link/back_end/platform_handler.py#L58)
method of the [`PlatformHandler`][ephys_link.back_end.platform_handler].
Use [New Scale Pathfinder MPM's binding][ephys_link.bindings.mpm_binding] as an example of how to do this.

## Test Your Binding

Once you've implemented your binding, you can test it by running Ephys Link using your binding
`ephys_link -b -t <cli_name>`. You can interact with it using the [Socket.IO API](socketio_api.md) or Pinpoint.

## Code standards

We use automatic static analyzers to check code quality. See
the [corresponding section in the code organization documentation](code_organization.md#static-analysis) for more
information.

## Submit Your Changes

When satisfied with your changes, submit a pull request to the main repository. We will review your changes and
merge them if they meet our standards!

Feel free to [reach out](../home/contact.md) to us if you have any questions or need help with your binding!