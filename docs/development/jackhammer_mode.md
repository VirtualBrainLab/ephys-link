# Jackhammer Mode

This is an internal feature for rapidly oscillating the manipulator along an axis.

Jackhammer mode is not exposed in Ephys Link yet so this guide is to demonstrate how to test it in Python.

## 1. Get Ephys Link

Follow the instructions for [Installing for Development](index.md#installing-for-development). Or, just use a basic Python virtual environment (Python 3.13+ is required):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install .
```

## 2. Change the Sensapex SDK to support Jackhammer Mode

You need to replace the `libum.dll` file in the Sensapex library folder. This is located at `<virtual env>\Lib\site-packages\sensapex`. If you made a virtual environment named `venv` in the previous step, it would be `.\venv\Lib\site-packages\sensapex`.

1. Download the custom SDK [here](../assets/libum.dll).
2. (Optional) Make a backup of the old `libum.dll` in the Sensapex library folder by renaming it to `libum.dll.bck` or something like that.
3. Copy the downloaded `libum.dll` to the Sensapex library folder.
4. Modify `sensapex.py` in the Sensapex library folder to enable using this custom DLL. Set the `max_version` variable at line `398` to `(1, 510)`.

You can (optionally) test if everything is still working by [running Ephys Link](../usage/starting_ephys_link.md) and checking to see if it can still see and control Sensapex manipulators.

## 3. Use the test script

There's a test script in `scripts/jackhammer.py` that makes a call to Jackhammer mode.

In short, jackhammer mode enables open-loop control of the manipulators by letting you turn on and off the motors in a sequence. You can define a "first" and "second" stage to cycle between. When the "thrust length" argument is positive, the manipulator will move in the forward direction and when it is negative it will move backwards. Thrust length is not a real unit but is some percentage representing the amount of movement a step should take.