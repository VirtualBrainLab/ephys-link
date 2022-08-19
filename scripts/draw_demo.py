# noinspection PyPackageRequirements
import socketio

# Draw parameters
drop_depth = 10550
drive_speed = 5000
draw_speed = 4000

# Setup server connection
sio = socketio.Client()
sio.connect("http://localhost:8080")

# Setup manipulator
sio.emit("register_manipulator", 2)
sio.emit("bypass_calibration", 2)

# Home position
sio.emit(
    "goto_pos",
    {"manipulator_id": 2, "pos": [10000, 10000, 10000, 0], "speed": drive_speed},
)

# Move to 0, 0
sio.emit(
    "goto_pos", {"manipulator_id": 2, "pos": [0, 0, 10000, 0], "speed": drive_speed}
)

# Drop marker
sio.emit(
    "drive_to_depth", {"manipulator_id": 2, "depth": drop_depth, "speed": draw_speed}
)

# 20000, 0, 10000, 12000
sio.emit(
    "goto_pos",
    {"manipulator_id": 2, "pos": [20000, 0, 10000, drop_depth], "speed": draw_speed},
)

# 20000, 20000, 10000, 12000
sio.emit(
    "goto_pos",
    {
        "manipulator_id": 2,
        "pos": [20000, 20000, 10000, drop_depth],
        "speed": draw_speed,
    },
)

# 0, 20000, 10000, 12000
sio.emit(
    "goto_pos",
    {"manipulator_id": 2, "pos": [0, 20000, 10000, drop_depth], "speed": draw_speed},
)

# 0, 0, 10000, 12000
sio.emit(
    "goto_pos",
    {"manipulator_id": 2, "pos": [0, 0, 10000, drop_depth], "speed": draw_speed},
)

# Raise marker
sio.emit("drive_to_depth", {"manipulator_id": 2, "depth": 0, "speed": drive_speed})

# Home position
sio.emit(
    "goto_pos",
    {"manipulator_id": 2, "pos": [10000, 10000, 10000, 0], "speed": drive_speed},
)
