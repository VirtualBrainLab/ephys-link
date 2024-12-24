By the end of this section, you will be able to add a manipulator platform to Ephys Link and control it using the server
API. This is a software development guide and assumes you have experience with Python.

## Set Up for Development

1. Fork the [Ephys Link repository](https://github.com/VirtualBrainLab/ephys-link).
2. Follow the instructions for [installing Ephys Link for development](index.md/#installing-for-development) to get all
   the necessary dependencies and tools set up. In this case, you'll want to clone your fork.

## Create a Manipulator Binding

Manipulators are added to Ephys Link through bindings. A binding is a Python class that extends the abstract base class
`BaseBinding` and it defines the functions Ephys Link expects from a platform.

Create a new Python module in `src/ephys_link/bindings` for your manipulator. Make a class that extends
`BaseBinding`. Most IDE's will automatically import the necessary classes and tell you the methods you need to
implement. These functions have signature documentation describing what they should do.

As described in the [system overview](../home/how_it_works.md), Ephys Link converts all manipulator movement into a
common "unified space" which is
the [left-hand cartesian coordinate system](https://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/geometry/coordinate-systems.html).
The two functions `platform_space_to_unified_space` and `unified_space_to_platform_space` are used to convert between
your manipulator's coordinate system and the unified space.

!!! tip

    See
    the [Sensapex uMp-4](https://github.com/VirtualBrainLab/ephys-link/blob/main/src/ephys_link/bindings/ump_4_bindings.py)
    binding for an example where the platform has a Python API (Sensapex's SDK) and
    the [New Scale Pathfinder MPM](https://github.com/VirtualBrainLab/ephys-link/blob/main/src/ephys_link/bindings/mpm_bindings.py)
    binding for an example where the platform uses a REST API to an external provider.

## Register the Binding

To make Ephys Link aware of your new binding, you'll need to register it in
`src/ephys_link/back_end/platform_handler.py`. In the function [
`_match_platform_type`](https://github.com/VirtualBrainLab/ephys-link/blob/c00be57bb552e5d0466b1cfebd0a54d555f12650/src/ephys_link/back_end/platform_handler.py#L69),
add a new `case` to the `match` statement that returns an instance of your binding when matched to the desired CLI name
for your platform. For example, to use Sensapex's uMp-4 the CLI launch command is `ephys_link.exe -b -t ump-4`,
therefore the matching case statement is `ump-4`.

## Test Your Binding

Once you've implemented your binding, you can test it by running Ephys Link using your binding
`ephys_link -b -t <your_manipulator>`. You can interact with it using the Socket.IO API or Pinpoint.

## Submit Your Changes

When you're satisfied with your changes, submit a pull request to the main repository. We will review your changes and
merge them if they meet our standards!

Feel free to [reach out](../home/contact.md) to us if you have any questions or need help with your binding!