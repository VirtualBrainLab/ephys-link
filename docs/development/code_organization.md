# Code Organization

This section gives an overview of Ephys Link's internal architecture. It is intended for
maintainers of Ephys Link.

## File Structure

Ephys Link starts from the `__main__.py` file. It imports each component of the application and calls the launch
sequence.

### Where to find things

- `back_end`: the Socket.IO server and the manipulator API.
- `front_end`: configuration GUI and CLI definition.
- `bindings`: manipulator binding implementations.
- `utils`: common utilities and helper functions (including
  [the base binding abstract base class][ephys_link.utils.base_binding]).

## Control Flow

As described in ["How It Works"](../home/how_it_works.md), Ephys Link is primarily a server that responds to events. The
server exposes the events and pass them to the chosen manipulator binding. Everything is asynchronous and uses callbacks
to return responses to the clients when ready.

[`PlatformHandler`][ephys_link.back_end.platform_handler] is responsible for converting between the server API and the
manipulator binding API. Because of this module, you don't have to worry about the details of the server API when
writing a manipulator binding.

## Static Analysis

The project is strictly type checked using [`hatch fmt` (ruff)](https://hatch.pypa.io/1.9/config/static-analysis/)
and [basedpyright](https://docs.basedpyright.com/latest/). All PR's are checked against these tools.

While they are very helpful in enforcing good code, they can be annoying when working with libraries that inherently
return `Any` (like HTTP requests) or are not strictly statically typed. In those situations we have added inline
comments to ignore specific checks. We try to only use this in scenarios where missing typing information came from
external sources and were out of developer control. We also do not make stubs.

We encourage using the type checker as a tool to help strengthen your code and only apply inline comments to ignore
specific instances where external libraries cause errors. Do not use file-wide ignores.