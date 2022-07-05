import csv
# noinspection PyPackageRequirements
import socketio
import atexit

import time

# Setup sockets
sio = socketio.Client()
sio.connect('http://10.18.251.95:8080')

sio.emit('register_manipulator', 1)
sio.emit('bypass_calibration', 1)
sio.emit('register_manipulator', 2)
sio.emit('bypass_calibration', 2)

running = True
sleep_time = 1 / 120
movement_threshold = 0.1

prev_pos_1 = [-1, -1, -1, -1]
prev_pos_2 = [-1, -1, -1, -1]

# Setup CSV files
man_1 = open('data/man_1.csv', 'a', newline='')
man_2 = open('data/man_2.csv', 'a', newline='')

man_1_writer = csv.writer(man_1)
man_2_writer = csv.writer(man_2)

header = ['time', 'x', 'y', 'z', 'depth']
man_1_writer.writerow(header)
man_2_writer.writerow(header)


def record(manipulator_id: int, pos: list[float], error: str):
    if error == '':
        global prev_pos_1
        global prev_pos_2

        # Get files to work with
        dest = man_1 if manipulator_id == 1 else man_2
        writer = man_1_writer if manipulator_id == 1 else man_2_writer
        prev_pos = prev_pos_1 if manipulator_id == 1 else prev_pos_2

        # Check if update needed
        should_write = False
        for prev, cur in zip(prev_pos, pos):
            if abs(prev - cur) > movement_threshold:
                should_write = True
                break

        # Update if needed
        if should_write:
            writer.writerow([time.time()] + pos)
            dest.flush()
            if manipulator_id == 1:
                prev_pos_1 = pos
            else:
                prev_pos_2 = pos

        # Pull next position
        if running:
            time.sleep(sleep_time)
            sio.emit('get_pos', manipulator_id, callback=record)


@atexit.register
def cleanup(_, __):
    print("Cleaning up")
    global running
    running = False

    man_1.flush()
    man_2.flush()

    man_1.close()
    man_2.close()

    sio.disconnect()


print("Begin recording")
sio.emit('get_pos', 1, callback=record)
sio.emit('get_pos', 2, callback=record)
