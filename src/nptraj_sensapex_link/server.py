from aiohttp import web
import argparse
import common as com
import signal
import sensapex_handler as sh
# noinspection PyPackageRequirements
import socketio
import sys
from threading import Thread
from typing import Any

# Setup server
sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)
is_connected = False

# Parse arguments
parser = argparse.ArgumentParser(description='Sensapex link: a websocket '
                                             'interface for uMp '
                                             'Micromanipulators',
                                 prog='python -m nptraj-sensapex-link')
parser.add_argument('-d', '--debug', dest='debug', action='store_true',
                    help='Enable debug mode')
parser.add_argument('-p', '--port', type=int, default=8080, dest='port',
                    help='Port to listen on')
parser.add_argument('-s', '--serial', type=str, default=None, dest='serial',
                    help='Serial port to use')
parser.add_argument('--version', action='version', version='Sensapex Link '
                                                           'v0.0.6',
                    help='Print version and exit')
args = parser.parse_args()
com.set_debug(args.debug)


# Handle connection events
@sio.event
async def connect(sid, _, __):
    """
    Acknowledge connection to the server
    :param sid: Socket session ID
    :param _: WSGI formatted dictionary with request info (unused)
    :param __: Authentication details (unused)
    """
    print(f'[CONNECTION]:\t\t {sid}\n')

    global is_connected
    if not is_connected:
        is_connected = True
    else:
        return False


@sio.event
async def disconnect(sid):
    """
    Acknowledge disconnection from the server
    :param sid: Socket session ID
    """
    print(f'[DISCONNECTION]:\t {sid}\n')

    sh.reset()
    global is_connected
    is_connected = False


# Events
@sio.event
async def register_manipulator(_, manipulator_id: int) -> (int, str):
    """
    Register a manipulator with the server
    :param _: Socket session ID (unused)
    :param manipulator_id: ID of the manipulator to register
    :return: Callback parameters (manipulator_id, error message (on error))
    """
    com.dprint(f'[EVENT]\t\t Register manipulator: {manipulator_id}')

    return sh.register_manipulator(manipulator_id)


@sio.event
async def get_pos(_, manipulator_id: int) -> com.PositionalOutputData:
    """
    Position of manipulator request
    :param _: Socket session ID (unused)
    :param manipulator_id: ID of manipulator to pull position from
    :return: Callback parameters (manipulator ID, position in (x, y, z,
    w) (or an empty array on error), error message)
    """
    com.dprint(f'[EVENT]\t\t Get position of manipulator'
               f' {manipulator_id}')

    return sh.get_pos(manipulator_id)


@sio.event
async def goto_pos(_, data: com.GotoPositionInputDataFormat) -> \
        com.PositionalOutputData:
    """
    Move manipulator to position
    :param _: Socket session ID (unused)
    :param data: Data containing manipulator ID, position, and speed
    :return: Callback parameters (manipulator ID, position in (x, y, z,
    w) (or an empty tuple on error), error message)
    """
    try:
        manipulator_id = data['manipulator_id']
        pos = data['pos']
        speed = data['speed']

    except KeyError:
        manipulator_id = data['manipulator_id'] if 'manipulator_id' in data \
            else -1
        print(f'[ERROR]\t\t Invalid data for manipulator {manipulator_id}\n')
        return com.PositionalOutputData(manipulator_id, (), 'Invalid data '
                                                            'format')

    except Exception as e:
        manipulator_id = data['manipulator_id'] if 'manipulator_id' in data \
            else -1
        print(f'[ERROR]\t\t Error in goto_pos: {e}\n')
        return com.PositionalOutputData(manipulator_id, (), 'Error in '
                                                            'goto_pos')

    com.dprint(
        f'[EVENT]\t\t Move manipulator {manipulator_id} '
        f'to position {pos}'
    )

    return await sh.goto_pos(manipulator_id, pos, speed)


@sio.event
async def drive_to_depth(_, data: com.DriveToDepthInputDataFormat) \
        -> (int, float, str):
    """
    Drive to depth
    :param _: Socket session ID (unused)
    :param data: Data containing manipulator ID, depth, and speed
    :return: Callback parameters (manipulator ID, depth (or -1 on error),
    error message)
    """
    try:
        manipulator_id = data['manipulator_id']
        depth = data['depth']
        speed = data['speed']

    except KeyError:
        manipulator_id = data['manipulator_id'] if 'manipulator_id' in data \
            else -1
        print(f'[ERROR]\t\t Invalid data for manipulator {manipulator_id}\n')
        return manipulator_id, -1, 'Invalid data format'

    except Exception as e:
        manipulator_id = data['manipulator_id'] if 'manipulator_id' in data \
            else -1
        print(f'[ERROR]\t\t Error in drive_to_depth: {e}\n')
        return manipulator_id, -1, 'Error in drive_to_depth'

    com.dprint(
        f'[EVENT]\t\t Drive manipulator {manipulator_id} '
        f'to depth {depth}'
    )

    return await sh.drive_to_depth(manipulator_id, depth, speed)


@sio.event
async def set_inside_brain(_, data: com.InsideBrainInputDataFormat) -> \
        (int, bool, str):
    """
    Set the inside brain state
    :param _: Socket session ID (unused)
    :param data: Data containing manipulator ID and inside brain state
    :return: Callback parameters (manipulator ID, inside, error message)
    """
    try:
        manipulator_id = data['manipulator_id']
        inside = data['inside']

    except KeyError:
        manipulator_id = data['manipulator_id'] if 'manipulator_id' in data \
            else -1
        print(f'[ERROR]\t\t Invalid data for manipulator {manipulator_id}\n')
        return manipulator_id, False, 'Invalid data format'

    except Exception as e:
        manipulator_id = data['manipulator_id'] if 'manipulator_id' in data \
            else -1
        print(f'[ERROR]\t\t Error in inside_brain: {e}\n')
        return manipulator_id, False, 'Error in set_inside_brain'

    com.dprint(
        f'[EVENT]\t\t Set manipulator {manipulator_id} inside brain to '
        f'{"true" if inside else "false"}'
    )

    return sh.set_inside_brain(manipulator_id, inside)


@sio.event
async def calibrate(_, manipulator_id: int) -> (int, str):
    """
    Calibrate manipulator
    :param _: Socket session ID (unused)
    :param manipulator_id: ID of manipulator to calibrate
    :return: Callback parameters (manipulator ID, error message)
    """
    com.dprint(f'[EVENT]\t\t Calibrate manipulator'
               f' {manipulator_id}')

    return await sh.calibrate(manipulator_id, sio)


@sio.event
async def bypass_calibration(_, manipulator_id: int) -> (int, str):
    """
    Bypass calibration of manipulator
    :param _: Socket session ID (unused)
    :param manipulator_id: ID of manipulator to bypass calibration
    :return: Callback parameters (manipulator ID, error message)
    """
    com.dprint(f'[EVENT]\t\t Bypass calibration of manipulator'
               f' {manipulator_id}')

    return sh.bypass_calibration(manipulator_id)


@sio.event
async def set_can_write(_, data: com.CanWriteInputDataFormat) -> (
        int, bool, str):
    """
    Set manipulator can_write state
    :param _: Socket session ID (unused)
    :param data: Data containing manipulator ID and can_write brain state
    :return: Callback parameters (manipulator ID, can_write, error message)
    """
    try:
        manipulator_id = data['manipulator_id']
        can_write = data['can_write']
        hours = data['hours']

    except KeyError:
        manipulator_id = data['manipulator_id'] if 'manipulator_id' in data \
            else -1
        print(f'[ERROR]\t\t Invalid data for manipulator {manipulator_id}\n')
        return manipulator_id, False, 'Invalid data format'

    except Exception as e:
        manipulator_id = data['manipulator_id'] if 'manipulator_id' in data \
            else -1
        print(f'[ERROR]\t\t Error in inside_brain: {e}\n')
        return manipulator_id, False, 'Error in set_can_write'

    com.dprint(
        f'[EVENT]\t\t Set manipulator {manipulator_id} can_write state to '
        f'{"true" if can_write else "false"}'
    )

    return sh.set_can_write(manipulator_id, can_write, hours, sio)


@sio.event
async def stop(_) -> bool:
    """
    Stop all manipulators
    :param _: Socket session ID (unused)
    :return: True if successful, False otherwise
    """
    com.dprint('[EVENT]\t\t Stop all manipulators')

    return sh.stop()


@sio.on('*')
async def catch_all(_, data: Any) -> None:
    """
    Catch all event
    :param _: Socket session ID (unused)
    :param data: Data received from client
    :return: None
    """
    print(f'[UNKNOWN EVENT]:\t {data}')


# Handle server start
def launch() -> None:
    """Launch the server"""
    signal.signal(signal.SIGINT, close)
    Thread(target=sh.poll_serial, args=(args.serial,)).start()
    web.run_app(app, port=args.port)


def close(_, __):
    """Close the server"""
    print('[INFO]\t\t Closing server')
    sh.continue_polling = False
    sh.stop()
    sys.exit(0)


if __name__ == '__main__':
    launch()
