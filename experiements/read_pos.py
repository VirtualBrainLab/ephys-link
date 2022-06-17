from sensapex import UMP

# Init and get device 1
ump = UMP.get_ump()
dev_ids = ump.list_devices()
if 1 not in ump.list_devices():
    print("Device 1 not found")
    exit(1)
manipulator_1 = ump.get_device(1)

# Calibrate
# manipulator_1.calibrate_zero_position()

# Read position
pos = manipulator_1.get_pos()
while True:
    new_pos = manipulator_1.get_pos()
    if new_pos != pos:
        print(new_pos)
        pos = new_pos
