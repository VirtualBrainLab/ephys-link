from ctypes import c_char, c_int

from sensapex import UMP

um = UMP.get_ump()

dev_id = 3
axis = 3

um.call("um_take_jackhammer_step", c_int(dev_id), c_char(axis), c_int(20), c_int(10), c_int(50), c_int(5), c_int(-50))
