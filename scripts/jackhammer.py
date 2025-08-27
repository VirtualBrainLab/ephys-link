from ctypes import c_char, c_int

from sensapex import UMP

um = UMP.get_ump()

dev_id = 3
axis = 3

um.call("um_take_jackhammer_step",
        c_int(dev_id), # Device number
        c_char(axis), # Axis (0=X, 1=Y, 2=Z, 3=D)
        c_int(20), # Number of cycles
        c_int(10), # Number of steps in first-stage
        c_int(15), # Thrust length
        c_int(5), # Number of steps in second-stage
        c_int(-15)) # Thrust length
