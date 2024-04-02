#!/usr/bin/python

########################################################################
# V1.0
########################################################################


'''
import sys
import time
import can



can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan', bitrate=250000)

canID=1280
cnt=0
cd=1
while 1:
#  try:
    msg = can.Message(arbitration_id=canID, data=[cd], extended_id=False)
    can0.send(msg)

    time.sleep(1)

    print("Message: {} Data: {}  counter: {}".format(canID,cd,cnt) )

    canID=canID+1
    cnt=cnt+1
    cd=cd+1
    if canID > 1283:
      canID = 1280

    if cd > 10:
      cd = 1
#  exception ValueError:
#    print("hello")
'''
import os
import can
import time

can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan', bitrate=250000)
'''
BYTE1 Maximum allowable charging voltage, high byte
BYTE2 Maximum allowable charging voltage, low byte
BYTE1&2 0.1V/bit Offset 0 example Vset=3201 Voltage: 320.1

BYTE3 Maximum allowable charging current, high byte
BYTE4 Maximum allowable charging current, low byte
BYTE3&4 0.1A/bit Offset 0 example Iset=582 Current: 58.2A

BYTE5 0: Charger start charging, 1: Battery protection Charger Stop Output, 2: Heating mode
BYTE6 SOC 0~100, example SOC=50, express SOC = 50%
BYTE7 Reserve
BYTE8 Reserve
'''  

Ladeschlussspannung = 54.6*10
Ladestrom = 10*10
Regler = 0 #0: Charger start charging, 1: Battery protection Charger Stop Output, 2: Heating mode
SoC = 70
data_Ladegeraet =int(Ladeschlussspannung).to_bytes(2, 'big') + int(Ladestrom).to_bytes(2, 'big') + int(Regler).to_bytes(1, 'big') + int(SoC).to_bytes(1, 'big') + int(0).to_bytes(2, 'big')
msg = can.Message(data=data_Ladegeraet, arbitration_id=0X1806E5F4, is_extended_id=True)
can0.send(msg)
print(msg)


print ('Laden beendet')