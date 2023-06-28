#!/usr/bin/python

########################################################################
# V1.0
########################################################################


import serial
import time
import threading
from multiprocessing import Queue
import enum
import numpy as np
import can
import logging

class Request(enum.Enum):
    NONE = 0
    BASIC_INFO = 1
    CELL_VOLTAGE = 2


class ProfinettoCAN(threading.Thread):
    def __init__(self, debugOutput, updateCycle, outCANfromProfinet):
        threading.Thread.__init__(self)
        self.debugOutput = debugOutput
        self.updateCycle = updateCycle
        self.outCANfromProfinet = outCANfromProfinet

        self.readcan = can.interface.Bus(channel = 'can0', bustype = 'socketcan', bitrate=250000, can_filters = [{"can_id": 0x500 , "can_mask": 0x7FF, "extended": False}])

        self.Request_AUX2 = None
        self.Request_P = None
        self.Request_C = None
        self.Request_sleep = None
        self.Status_receive = None
        
    def receiveCANfromProfinet(self):
        msg = self.readcan.recv(1)
        #print(msg)
        self.Status_receive = int.from_bytes(msg.data[0:1], 'big')

        #Bit1 AUX2
        if bin(self.Status_receive>>0)[-1]=='0':
            self.Request_AUX2 = 0
        else:
            self.Request_AUX2 = 1
            
        #Bit1 Freigabe P+
        if bin(self.Status_receive>>1)[-1]=='0':
            self.Request_P = 0
        else:
            self.Request_P = 1
            
        #Bit2 Ladefreigabe
        if bin(self.Status_receive>>2)[-1]=='0':
            self.Request_C = 0
        else:
            self.Request_C = 1
        #Bit3 Request Sleep
        if bin(self.Status_receive>>3)[-1]=='0':
            self.Request_sleep = 0
        else:
            self.Request_sleep = 1
            
        self.Requests = {'Request_AUX2':self.Request_AUX2,'Request_P':self.Request_P, 'Request_C':self.Request_C, 'Request_sleep':self.Request_sleep}

        self.outCANfromProfinet.put(self.Requests)
        
    def printreceiveCANfromProfinet(self):
        print("receice CAN Data")
        print("_________________________________________________")
        print(self.Requests)
        
        #Bit1 AUX2
        if self.Request_AUX2 == 0:
            print('Bit0 = 0 -> AUX2 inaktiv')
        else:
            print('Bit0 = 1 -> AUX2 aktiv')
            
        #Bit1 Freigabe P+
        if self.Request_P == 0:
            print('Bit1 = 0 -> P+ inaktiv')
        else:
            print('Bit1 = 1 -> P+ aktiv')
            
        #Bit2 Ladefreigabe
        if self.Request_C == 0:
            print('Bit2 = 0 -> C+ inaktiv')
        else:
            print('Bit2 = 1 -> C+ aktiv')
        
        #Bit3 Request Sleep
        if self.Request_sleep == 0:
            print('Bit3 = 0 -> nichts passiert')
        else:
            print('Bit3 = 1 -> Akku wird abgeschalten')
        
        
    def run(self):
        if self.debugOutput:
            print("can: Run - Start Thread")
        incData = []
        self.running = True
        incomingDataTime = int(round(time.time() * 1000))
    
        while(self.running):
            time.sleep(.01)   #wichtig sonst 100% cpu auslastung
            #check for incoming data from main thread
            try:
                #if(self.sendInProgress==False):
                self.receiveCANfromProfinet()
                #self.printreceiveCANfromProfinet()
                
                
            except:
                # do nothing
                pass

        if self.debugOutput:
                print("canO: Thread exit")
