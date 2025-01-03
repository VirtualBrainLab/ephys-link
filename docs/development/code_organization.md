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
