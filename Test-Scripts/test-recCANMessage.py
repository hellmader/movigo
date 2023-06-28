#!/usr/bin/python

########################################################################
# V1.0
########################################################################


import os
import can
import time


#CAN_filter = [{"can_id": 0x18FF50E5 , "can_mask": 0x1FFFFFFF, "extended": True}]
#can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan_ctypes', bitrate=250000, can_filters = CAN_filter)



CAN_filter = [{"can_id": 0x500 , "can_mask": 0x7FF, "extended": False}]
can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan', can_filters = CAN_filter)# socketcan_native
#can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan_ctypes', can_filters = CAN_filter)# socketcan_native

while True:
  message = can0.recv()
  c = '{0:f} {1:x} {2:x} '.format(message.timestamp, message.arbitration_id, message.dlc)
  s=''
  for i in range(message.dlc ):
    s +=  '{0:x} '.format(message.data[i])
    print(' {}'.format(c+s))
