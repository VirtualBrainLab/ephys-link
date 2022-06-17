import time

from sensapex import UMP
import time

# Init and get devices 1 and 2
ump = UMP.get_ump()
dev_ids = ump.list_devices()

if 1 not in ump.list_devices():
    print("Device 1 not found")
    exit(1)
manipulator_1 = ump.get_device(1)

if 2 not in ump.list_devices():
    print("Device 1 not found")
    exit(1)
manipulator_2 = ump.get_device(2)

# Move
print("Moving to 0")
move_1 = ump.goto_pos(1, [0, 0, 0, 0], 2000)
time.sleep(6)
move_2 = ump.goto_pos(2, [0, 0, 0, 0], 2000)

move_1.finished_event.wait()
move_2.finished_event.wait()
print("Move finished")

print("Moving back to home")
move_1 = ump.goto_pos(1, [10000, 10000, 10000, 10000], 2000)
move_2 = ump.goto_pos(2, [10000, 10000, 10000, 10000], 2000)

move_1.finished_event.wait()
move_2.finished_event.wait()
print("Move finished")

ump.close()
