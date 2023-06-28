#!/usr/bin/python

########################################################################
# V1.0
########################################################################

import serial
import time
import threading
import enum
import can
import logging
from clHelper import checkTime
import time


class Request(enum.Enum):
    NONE = 0
    BASIC_INFO = 1
    CELL_VOLTAGE = 2


def current_milli_time():
    return round(time.time() * 1000)
#,{"can_id":0x18FF50E5, "can_mask": 0x1FFFFFFF, "extended": True},{"can_id":0x1806E5F4, "can_mask": 0x1FFFFFFF, "extended": True}
class readCan(threading.Thread):
    def __init__(self, debugOutput, updateCycle, outCAN):
        threading.Thread.__init__(self)
        self.debugOutput = debugOutput
        self.updateCycle = updateCycle
        self.outCAN = outCAN
        can_filters = [{"can_id":0x1A8, "can_mask": 0x7FF, "extended": False},{"can_id":0x2A8, "can_mask": 0x7FF, "extended": False},{"can_id":0x3A8, "can_mask": 0x7FF, "extended": False},{"can_id":0x4A8, "can_mask": 0x7FF, "extended": False},{"can_id":0x228, "can_mask": 0x7FF, "extended": False},{"can_id":0x18FF50E5, "can_mask": 0x1FFFFFFF, "extended": True},{"can_id":0x1806E5F4, "can_mask": 0x1FFFFFFF, "extended": True}]
        self.can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan', bitrate=500000, can_filters = can_filters)
        self.reg1 = 0x0
        self.reg1_time = 0
        self.reg2 = 0x0
        self.reg2_time = 0
        self.reg3 = 0x0
        self.reg3_time = 0
        self.reg4 = 0x0
        self.reg4_time = 0
        self.regplc = 0x0
        self.regplc_time = 0
        self.regrchg = 0x0
        self.regrchg_time = 0
        self.regwchg = 0x0
        self.regwchg_time = 0
        self.reg = {'0x1A8':self.reg1,'time 0x1A8':self.reg1_time,'0x2A8':self.reg2,'time 0x2A8':self.reg2_time,'0x3A8':self.reg3,'time 0x3A8':self.reg3_time,'0x4A8':self.reg4,'time 0x4A8':self.reg4_time,'0x228':self.regplc,'time 0x228':self.regplc_time,'0x18FF50E5':self.regrchg,'time 0x18ff50e5':self.regrchg_time,'0x1806E5F4':self.regwchg,'time 0x1806E5F4':self.regwchg_time}

    
    def readCanMsg(self):
        self.reg = {'0x1A8':self.reg1,'time 0x1A8':self.reg1_time,'0x2A8':self.reg2,'time 0x2A8':self.reg2_time,'0x3A8':self.reg3,'time 0x3A8':self.reg3_time,'0x4A8':self.reg4,'time 0x4A8':self.reg4_time,'0x228':self.regplc,'time 0x228':self.regplc_time,'0x18FF50E5':self.regrchg,'time 0x18ff50e5':self.regrchg_time,'0x1806E5F4':self.regwchg,'time 0x1806E5F4':self.regwchg_time}
        

        
        try:
            self.outCAN.put(self.reg)
        except:
            pass
        
    def run(self):
        if self.debugOutput:
            print("can: Run - Start Thread")
        incData = []
        self.running = True

        t1 = checkTime() 
        
        time1A8 = time.time()
        time2A8 = time.time()
        time3A8 = time.time()
        time4A8 = time.time()
        time228 = time.time()
        time18FF50E5 = time.time()
        time1806e5f4 = time.time()
         
        while(self.running):
            time.sleep(.01)   #wichtig sonst 100% cpu auslastung
            #check for incoming data from main thread

            try:
                #print('I tryyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy')
                msg = self.can0.recv(2)  #lese cannachrichten  ohne timeout fuer ladegeraet ein
                #print('MSG',msg)
                
                try:
                    self.reg1_time = time.time() - time1A8    
                    self.reg2_time = time.time() - time2A8
                    self.reg3_time = time.time() - time3A8
                    self.reg4_time = time.time() - time4A8
                    self.regplc_time = time.time() - time228
                    self.regrchg_time = time.time() - time18FF50E5
                    self.regwchg_time = time.time() - time1806e5f4
                    #print('ARBID',hex(msg.arbitration_id))
                    if str(hex(msg.arbitration_id))=='0x1a8':
                        #self.readCanMsg({'0x1A8':msg})
                        msg_data = str(hex(int.from_bytes(msg.data, 'big')))
                        self.reg1=msg_data
                        self.reg1_time = time.time() - time1A8
                        time1A8 = time.time()
                        
                        #print('REG1',self.reg1)                    
                    elif str(hex(msg.arbitration_id))=='0x2a8':
                        #self.readCanMsg({'0x2A8':msg})
                        msg_data = str(hex(int.from_bytes(msg.data, 'big')))
                        self.reg2=msg_data
                        self.reg2_time = time.time() - time2A8
                        time2A8 = time.time()
                                                
                    elif str(hex(msg.arbitration_id))=='0x3a8':
                        #self.readCanMsg({'0x3A8':msg})
                        msg_data = str(hex(int.from_bytes(msg.data, 'big')))
                        self.reg3=msg_data
                        self.reg3_time = time.time() - time3A8
                        time3A8 = time.time()
                          
                    elif str(hex(msg.arbitration_id))=='0x4a8':
                        #self.readCanMsg({'0x4A8':msg})
                        msg_data = str(hex(int.from_bytes(msg.data, 'big')))
                        self.reg4=msg_data
                        self.reg4_time = time.time() - time4A8
                        time4A8 = time.time()
                        
                    elif str(hex(msg.arbitration_id))=='0x228':
                        #self.readCanMsg({'0x228':msg})
                        msg_data = str(hex(int.from_bytes(msg.data, 'big')))
                        self.regplc=msg_data
                        self.regplc_time = time.time() - time228
                        time228 = time.time()
                        
                    elif str(hex(msg.arbitration_id))=='0x18ff50e5':
                        #self.readCanMsg({'0x18FF50E5':msg})
                        msg_data = str(hex(int.from_bytes(msg.data, 'big')))
                        self.regrchg=msg_data
                        self.regrchg_time = time.time() - time18FF50E5
                        time18FF50E5 = time.time()
                        
                    elif str(hex(msg.arbitration_id))=='0x1806e5f4':
                        #self.readCanMsg({'0x1806E5F4':msg})
                        msg_data = str(hex(int.from_bytes(msg.data, 'big')))
                        self.regwchg=msg_data
                        self.regwchg_time = time.time() - time1806e5f4
                        time1806e5f4 = time.time()
                    

                      
                except:
                    #print('Exception 2')
                    pass           
            except:
                print('Exception First Try')
                pass
                
            self.readCanMsg()
            

        if self.debugOutput:
                print("canO: Thread exit")
                        



