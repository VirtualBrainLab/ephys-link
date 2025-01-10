# Using Ephys Link

Ephys Link is designed to interact with other software. Any [Socket.IO](https://socket.io/) client application can talk
to Ephys Link and access connected manipulators. [Pinpoint](https://github.com/VirtualBrainLab/Pinpoint) is a first-party application that does just that!

!!! info "Stop All Movement"

    As you start using Ephys Link with other software you may want to stop all manipulators in case of an emergency.
    <br/><br/>
    Press the keyboard shortcut <kbd>ctrl</kbd> + <kbd>shift</kbd> + <kbd>alt</kbd> + <kbd>q</kbd> to "quit" all
    movement.

## Connecting to Pinpoint

[Pinpoint](https://github.com/VirtualBrainLab/Pinpoint) is a tool for planning electrophysiology recordings and other
_in vivo_ insertions, as well as tracking the position of probes in real-time inside the brain.

Ephys Link was developed alongside Pinpoint to facilitate tracking and positioning of manipulators. Follow the
[instructions on Pinpoint's documentation](https://virtualbrainlab.org//pinpoint/tutorials/tutorial_ephys_link.html) to
use Ephys Link inside Pinpoint!

## Experiment Automation

Pinpoint and Ephys Link can work together to automate manual procedures in electrophysiology experiments. Follow the
[instructions on Pinpoint's documentation](https://virtualbrainlab.org//pinpoint/tutorials/tutorial_ephys_copilot.html)
to use automation in your next experiment!

!!! note

    Automation is still in early development. We recommend [contacting](https://virtualbrainlab.org/about/overview.html)
    Dan Birman and Kenneth Yang if you would like to try it out!