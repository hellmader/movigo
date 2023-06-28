import time
from clHelper import checkTime
import os
import can


t1 = checkTime()


#Testadresse isendet folgende ID und daten: 0x12345678 mit Daten 00 11 22 33 44 55 66 77 (Hex value)
can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan', is_extended_id=True)



canID=0x12345678
cd=[0x00,0x11,0x22,0x33,0x44,0x55,0x66,0x77]


while True:
  msg = can.Message(arbitration_id=canID, data=cd, is_extended_id=True)
  can0.send(msg)
  print("Send CAN Message...")
  time.sleep(1)
 


