import atexit
import csv
import os.path
import time

# noinspection PyPackageRequirements
import socketio

from src.ephys_link import PositionalOutputData

# Parameters
MANIPULATOR_ID = 2
IP = "localhost"
PORT = 8080
HOME_POSITION = [10, 10, 10, 10]  # in mm

MOVEMENT_SPEED = 1
RESET_SPEED = 1000  # in um/s
TARGET_AXIS = 0  # 0 = X, 1 = Y, 2 = Z, 3 = Depth
TARGET_POS = 15  # in mm
FILE_NAME_EXT = "x1"

# Start time record
START_TIME = -1

# Setup server connection
sio = socketio.Client()
# noinspection HttpUrlsUsage
sio.connect(f"http://{IP}:{PORT}")

# Setup manipulator
sio.emit("register_manipulator", MANIPULATOR_ID)
sio.emit("bypass_calibration", MANIPULATOR_ID)
sio.emit(
    "set_can_write",
    {"manipulator_id": MANIPULATOR_ID, "can_write": True, "hours": 1},
)

# Setup output file and data dir
if not os.path.exists("data"):
    os.makedirs("data")
file = open(f"data/crash_test_{FILE_NAME_EXT}.csv", "a", newline="")
writer = csv.writer(file)
writer.writerow(["time (ms)", "x", "y", "z", "depth"])
file.flush()


# Define cleanup function
@atexit.register
def cleanup(_, __):
    print("Cleaning up...")
    file.flush()
    file.close()
    sio.disconnect()


# Define recording function
def record_position(data: PositionalOutputData):
    if data["error"] == "":
        writer.writerow([(time.time() * 1000) - START_TIME, *data["position"]])
        file.flush()
        sio.emit("get_pos", MANIPULATOR_ID, callback=record_position)


# Move to 0, 0, 0, 0
sio.emit(
    "goto_pos",
    {"manipulator_id": MANIPULATOR_ID, "pos": HOME_POSITION, "speed": RESET_SPEED},
)

# Set target location
target_location = HOME_POSITION
target_location[TARGET_AXIS] = TARGET_POS

# Update start time
START_TIME = time.time() * 1000

# Drive
sio.emit(
    "goto_pos",
    {"manipulator_id": MANIPULATOR_ID, "pos": target_location, "speed": MOVEMENT_SPEED},
)

# Record data
sio.emit("get_pos", MANIPULATOR_ID, callback=record_position)
