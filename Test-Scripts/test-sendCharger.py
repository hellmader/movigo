#!/usr/bin/python

########################################################################
# V1.0
########################################################################


import sys
import time
import can

#    cansend can0 1806E5F4#15.54.00.32.00.32.00.00

can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan', bitrate=250000)

canID=0x1806E5F4
cnt=0
cd=[0x15,0x54,0x00,0x32,0x00,0x32,0x00,0x00]
while 1:
#  try:
    #msg = can.Message(arbitration_id=canID, data=cd, extended_id=True)
    msg = can.Message(arbitration_id=canID, data=cd, is_extended_id=True)
    can0.send(msg)

    time.sleep(1)

    print("Message: {} Data: {}  counter: {}".format(canID,cd,cnt) )

    cnt=cnt+1
#  exception ValueError:
#    print("hello")

