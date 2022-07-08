import argparse
import csv
# noinspection PyPackageRequirements
import socketio
import atexit
import os
import time

# Parse arguments
parser = argparse.ArgumentParser(description='Read and record position into '
                                             'CSV files',
                                 prog='python read_to_file.py')
parser.add_argument('-i', '--ip', type=str, default='localhost', dest='ip',
                    help='IP address to listen on')
parser.add_argument('-p', '--port', type=int, default=8080, dest='port',
                    help='Port to listen on')
parser.add_argument('-m', '--manipulators', type=str, default='1,2',
                    dest='manipulators',
                    help='Manipulator IDs, separated by commas with no spaces')
args = parser.parse_args()


class ManipulatorMeta:
    """Metadata for a manipulator"""

    def __init__(self, man_id: int):
        """
        Construct a ManipulatorMeta object
        :param man_id: Manipulator ID
        """
        # File
        file_exists = os.path.exists(f'data/{man_id}.csv')
        self.file = open(f'data/{man_id}.csv', 'a', newline='')
        self.writer = csv.writer(self.file)
        if not file_exists:
            self.writer.writerow(['time (sec)', 'x', 'y', 'z', 'depth'])

        # Previous position
        self.prev_pos = [-1, -1, -1, -1]


# Setup data directory
if not os.path.exists('data'):
    os.makedirs('data')

# Extract manipulators
manipulators = None
try:
    manipulators = {int(m): ManipulatorMeta(int(m)) for m in
                    args.manipulators.split(',')}
except ValueError:
    print('Invalid manipulator IDs')
    exit(1)
except Exception as e:
    print(e)
    exit(1)

# Setup sockets
sio = socketio.Client()
try:
    # noinspection HttpUrlsUsage
    sio.connect(f'http://{args.ip}:{args.port}')
except Exception as e:
    print(f'Invalid IP address or port: {e}')
    exit(1)


def register_manipulators():
    """Register and bypass calibration for all manipulators"""
    for man_id in manipulators.keys():
        sio.emit('register_manipulator', man_id)
        sio.emit('bypass_calibration', man_id)


# Setup operations
running = True
sleep_time = 1 / 120
movement_threshold = 0.1
start_time = time.time()


def record(man_id: int, pos: list[float], error: str):
    if error == '':
        # Get files to work with
        manipulator = manipulators[man_id]
        dest = manipulator.file
        writer = manipulator.writer
        prev_pos = manipulator.prev_pos

        # Check if update needed
        should_write = False
        for prev, cur in zip(prev_pos, pos):
            if abs(prev - cur) > movement_threshold:
                should_write = True
                break

        # Update if needed
        if should_write:
            writer.writerow([time.time() - start_time] + pos)
            dest.flush()
            manipulator.prev_pos = pos
    elif error == 'Manipulator not registered':
        sio.emit('register_manipulator', man_id)
        sio.emit('bypass_calibration', man_id)

    # Pull next position
    if running:
        time.sleep(sleep_time)
        sio.emit('get_pos', man_id, callback=record)


@atexit.register
def cleanup(_, __):
    print("Cleaning up")
    global running
    running = False

    for manipulator in manipulators:
        manipulator.file.flush()
        manipulator.file.close()

    sio.disconnect()


print("Begin recording")
for manipulator_id in manipulators.keys():
    sio.emit('get_pos', manipulator_id, callback=record)
    sio.emit('get_pos', manipulator_id, callback=record)
