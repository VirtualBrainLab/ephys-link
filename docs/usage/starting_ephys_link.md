# Starting Ephys Link

Ephys Link is a server that runs in the background.

!!! info

    Most people should use Ephys Link through Pinpoint. See documentation
    on [connecting from Pinpoint](using_ephys_link.md#connecting-to-pinpoint) and using Ephys Link
    for [experiment automation](using_ephys_link.md#experiment-automation).

If you are building a client application that will talk to Ephys Link, see
the [Socket.IO API reference](../development/socketio_api.md).

There are different ways of launching Ephys Link depending on its installation.

## Standalone Executable (GUI)

1. Double-click the executable file to launch the configuration window.
    1. Take note of the IP address and port. **Copy this information into Pinpoint to connect**.
2. Select the desired configuration and click "Launch Server".

The configuration window will close and the server will launch. Your configurations will be saved for future use.

To connect to the server from Pinpoint, provide the IP address and port. For example, if the server is running on the
same computer that Pinpoint is, use

- Server: `localhost`
- Port: `3000`

If the server is running on a different (local) computer, use the IP address of that computer as shown in the startup
window instead of `localhost`.

## Standalone Executable (CLI)

Ephys Link can be launched from the command line directly without the
configuration window. This is useful for computers
or servers without graphical user interfaces.

With the standalone executable downloaded, invoking the executable from the
command line:

```bash
EphysLink-vX.X.X.exe -b
```

Use the actual name of the executable you downloaded. The `-b` or `--background` flag will launch the server without the
configuration window and read configuration from CLI arguments.

Here are some examples of how to start Ephys Link with a specific platform (replace `EphysLink.exe` with the actual name
of the executable you downloaded):

| Manipulator Platform                   | Command                              |
|----------------------------------------|--------------------------------------|
| Sensapex uMp-4 (default)               | `EphysLink.exe -b`                   |
| New Scale Pathfinder MPM Control v2.8+ | `EphysLink.exe -b -t pathfinder-mpm` |

More options can be viewed by running `EphysLink.exe -h`.

## Python Package

Ephys Link can be invoked from the command line with the same arguments as the standalone executable using the
`ephys-link` binary (or `el` for short).