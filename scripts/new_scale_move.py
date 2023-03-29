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
y = ctrl.GetAxis(1)

# Setup motion
x.SetCL_Enable(True)
x.SetCL_Speed(4000, 5000, 5)
y.SetCL_Enable(True)
y.SetCL_Speed(4000, 5000, 5)

target_pos = random.randint(0, 15000)
x.MoveAbsolute(target_pos)
y.MoveAbsolute(target_pos)
print("Target:", target_pos)

AT_TARGET_FLAG = 0x040000

done_event = threading.Event()


def check_done():
    x.QueryPosStatus()
    y.QueryPosStatus()
    while not x.CurStatus & AT_TARGET_FLAG and not y.CurStatus & AT_TARGET_FLAG:
        time.sleep(0.1)
        x.QueryPosStatus()
        y.QueryPosStatus()
    done_event.set()


threading.Thread(target=check_done).start()

done_event.wait()

x.QueryPosStatus()
y.QueryPosStatus()
print("Current pos x:", x.CurPosition)
print("Current pos y:", y.CurPosition)

ctrl.Disconnect()
