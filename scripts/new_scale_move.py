from pythonnet import load

load("netfx")

import clr

clr.AddReference("../ephys_link/resources/NstMotorCtrl")

import random
import time
import math
import threading

# noinspection PyUnresolvedReferences
from NstMotorCtrl import NstCtrlHostIntf

ctrl = NstCtrlHostIntf()

ctrl.Ports = "USB1,USB2"

print(ctrl.Initialize())

x = ctrl.GetAxis(0)

# Start motion
x.SetCL_Enable(True)
x.QueryPosStatus()
print(x.CurPosition)
x.SetCL_Speed(4000, 5000, 5)

target_pos = random.randint(0, 15000)
x.MoveAbsolute(target_pos)
print("Target:", target_pos)


def check_done(target, event):
    x.QueryPosStatus()
    pos = x.CurPosition
    while not math.isclose(pos, target, abs_tol=1):
        time.sleep(0.1)
        x.QueryPosStatus()
        pos = x.CurPosition
    event.set()


done_event = threading.Event()
thread = threading.Thread(target=check_done, args=(target_pos, done_event))
thread.start()

done_event.wait()

x.QueryPosStatus()
print("Current pos:", x.CurPosition)

ctrl.Disconnect()
