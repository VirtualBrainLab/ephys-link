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
sio.connect('http://localhost:8080')

sio.emit('register_manipulator', 1)
sio.emit('bypass_calibration', 1)
sio.emit('register_manipulator', 2)
sio.emit('bypass_calibration', 2)

prev_time = time.time()

running = True

# Setup CSV files
man_1 = open('man_1.csv', 'a', newline='')
man_2 = open('man_2.csv', 'a', newline='')

man_1_data = deque()
man_2_data = deque()

man_1_writer = csv.writer(man_1)
man_2_writer = csv.writer(man_2)


def record(manipulator_id: int, pos: list[float], error: str):
    global prev_time
    if error == '':
        dest = man_1_data if manipulator_id == 1 else man_2_data
        cur_time = time.time()
        dest.appendleft([cur_time, cur_time - prev_time] + pos)
        prev_time = cur_time


def save():
    while running:
        if len(man_1_data):
            man_1_writer.writerows(list(man_1_data))
            man_1_data.clear()
        if len(man_2_data):
            man_2_writer.writerow(list(man_2_data))
            man_2_data.clear()

    print("Saving last bits")
    if len(man_1_data):
        man_1_writer.writerows(list(man_1_data))
    if len(man_2_data):
        man_2_writer.writerow(list(man_2_data))

    man_1.close()
    man_2.close()
    print("Done")


def cleanup(_, __):
    global running
    running = False
    print("Stopping")
    sio.disconnect()
    sys.exit(0)


signal.signal(signal.SIGINT, cleanup)

threading.Thread(target=save).start()

print("Begin recording")
while running:
    sio.emit('get_pos', 1, callback=record)
    sio.emit('get_pos', 2, callback=record)
    # sio.sleep(0.016666)
