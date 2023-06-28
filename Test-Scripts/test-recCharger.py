#!/usr/bin/python

########################################################################
# V1.0
########################################################################


import os
import can
import time


#can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan_ctypes')# socketcan_native
CAN_filter = [{"can_id": 0x18FF50E5 , "can_mask": 0x1FFFFFFF, "extended": True}]
can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan', bitrate=250000, can_filters = CAN_filter)
#can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan_ctypes', bitrate=250000, can_filters = CAN_filter)
timer = 0

    
while timer < 10:
    timer = timer +1
    msg = can0.recv(2)
    if msg is None:
        print('kein Ladegerät da')
    else:
        print(msg)
        Spannung_Ladegeraet = int.from_bytes(msg.data[0:2], 'big') # 531 bedeutet 53,1V
        Strom_Ladegeraet = int.from_bytes(msg.data[2:4], 'big') # 280 bedeutet 28A
        Status_Ladegerät = int.from_bytes(msg.data[4:5], 'big')
        
        print ('Spannung: ', Spannung_Ladegeraet)
        print ('Strom: ', Strom_Ladegeraet)
        print ('Status: ', bin(Status_Ladegerät))
        
        #Bit0 Hardware Error 0: normal. 1: Hardware error
        if bin(Status_Ladegerät>>0)[-1]=='0':
            print('Bit0 = 0 -> normal')
        else:
            print('Bit0 = 1 -> Harware error')
        #Bit1 Charger Temperature 0: normal. 1: Charger over temperature protection
        if bin(Status_Ladegerät>>1)[-1]=='0':
            print('Bit1 = 0 -> normal')
        else:
            print('Bit1 = 1 -> Charger over temperature protection')
        #Bit2 Input Voltage 0: Input voltage normal. 1: Input voltage is wrong and the charger stops working
        if bin(Status_Ladegerät>>2)[-1]=='0':
            print('Bit2 = 0 -> Input voltage normal')
        else:
            print('Bit2 = 1 -> Input voltage is wrong and the charger stops working')
        #Bit3 Start state 0: the charger detects that the battery voltage enters the start state. 1: Is off. (used to prevent reverse connection of battery)
        if bin(Status_Ladegerät>>3)[-1]=='0':
            print('Bit3 = 0 -> the charger detects that the battery voltage enters the start state')
        else:
            print('Bit3 = 1 -> Is off. (used to prevent reverse connection of battery)')
        #Bit4 Communication status 0: communication is normal. 1: Communication receiving timeout
        if bin(Status_Ladegerät>>4)[-1]=='0':
            print('Bit4 = 0 -> communication is normal')
        else:
            print('Bit4 = 1 -> Communication receiving timeout')
        #Bit5 AGV Status 1
        #Bit6 AGV Status 2
        #Bit7 AGV Status 2
        



print ('Abfrage beendet')
