import threading
from collections import deque
import csv
import signal
# noinspection PyPackageRequirements
import socketio
import sys

import time

# Setup sockets
sio = socketio.Client()
sio.connect('http://10.18.251.95:8080')

sio.emit('register_manipulator', 1)
sio.emit('bypass_calibration', 1)
sio.emit('register_manipulator', 2)
sio.emit('bypass_calibration', 2)

running = True

# Setup CSV files
man_1 = open('data/man_1.csv', 'a', newline='')
man_2 = open('data/man_2.csv', 'a', newline='')

man_1_data = deque()
man_2_data = deque()

man_1_writer = csv.writer(man_1)
man_2_writer = csv.writer(man_2)

header = ['time', 'x', 'y', 'z', 'depth']
man_1_writer.writerow(header)
man_2_writer.writerow(header)


def record(manipulator_id: int, pos: list[float], error: str):
    if error == '':
        dest = man_1_data if manipulator_id == 1 else man_2_data
        dest.appendleft([time.time()] + pos)
        sio.emit('get_pos', manipulator_id, callback=record)


def save():
    while running:
        if len(man_1_data):
            man_1_writer.writerows(list(man_1_data))
            man_1_data.clear()
        if len(man_2_data):
            man_2_writer.writerow(list(man_2_data))
            man_2_data.clear()

    if len(man_1_data):
        man_1_writer.writerows(list(man_1_data))
    if len(man_2_data):
        man_2_writer.writerow(list(man_2_data))

    man_1.close()
    man_2.close()
    print("Finished saving")
    sys.exit(0)


def cleanup(_, __):
    global running
    running = False
    print("Stopping")
    sio.disconnect()
    sys.exit(0)


signal.signal(signal.SIGINT, cleanup)

threading.Thread(target=save).start()

print("Begin recording")
sio.emit('get_pos', 1, callback=record)
sio.emit('get_pos', 2, callback=record)
