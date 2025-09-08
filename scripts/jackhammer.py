from ctypes import c_char, c_int

from sensapex import UMP

# Edit these parameters:
DEVICE_ID = 3  # Manipulator ID.
AXIS = 3  # Axis (0=X, 1=Y, 2=Z, 3=D).

NUMBER_OF_CYCLES = 20  # Number of time the first and second stage are repeated.

NUMBER_OF_STEP_IN_FIRST_STAGE = 10
FIRST_STAGE_THRUST_LENGTH = 15  # +/- 0 - 100

NUMBER_OF_STEP_IN_SECOND_STAGE = 5
SECOND_STAGE_THRUST_LENGTH = -15  # +/- 0 - 100

# Do not edit below this line.
um = UMP.get_ump()

um.call(
    "um_take_jackhammer_step",
    c_int(DEVICE_ID),
    c_char(AXIS),
    c_int(NUMBER_OF_CYCLES),
    c_int(NUMBER_OF_STEP_IN_FIRST_STAGE),
    c_int(FIRST_STAGE_THRUST_LENGTH),
    c_int(NUMBER_OF_STEP_IN_SECOND_STAGE),
    c_int(SECOND_STAGE_THRUST_LENGTH),
)
