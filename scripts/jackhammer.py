from sensapex import UMP
from ctypes import c_int, c_char

um = UMP.get_ump()

dev_id = 3
axis = 3

for i in range(20):
    um.call("um_take_jackhammer_step", c_int(dev_id), c_char(axis), c_int(1), c_int(1), c_int(50), c_int(0), c_int(0))