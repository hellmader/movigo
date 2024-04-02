import serial
import time
import threading
from multiprocessing import Queue
import enum
import numpy as np
import can

class Request(enum.Enum):
    NONE = 0
    BASIC_INFO = 1
    CELL_VOLTAGE = 2


class UDP(threading.Thread):
    def __init__(self, debugOutput, updateCycle, inUDPfromMain, outUDPtoMain):
        threading.Thread.__init__(self)
        self.debugOutput = debugOutput
        self.updateCycle = updateCycle
        self.inUDPfromMain = inUDPfromMain
        self.outUDPtoMain = outUDPtoMain
        self.data = 0

        
    def sendUDP(self,data):
        self.data = data

    def receiveUDP(self):
        data=1
        self.outUDPtoMain.put(data)
        
        
    def printsendUDP(self):
        
        print('Data to UDP:   ',self.data)
        
        print("sent UDP Data")
        print("_________________________________________________")
        
    def run(self):
        if self.debugOutput:
            print("can: Run - Start Thread")
        incData = []
        self.running = True
        incomingDataTime = int(round(time.time() * 1000))

            
        
        while(self.running):
            #check for incoming data from main thread
            try:
                #if(self.sendInProgress==False):
                qDataIn = self.inUDPfromMain.get_nowait()
                
                if(qDataIn=="SIG-INT"):
                    # end thread
                    if self.debugOutput:
                        print("Can: End - SIG-INT arrived")
                    self.running = False
                    
                elif(qDataIn!=None):
                    self.sendUDP(qDataIn)
                    self.printsendUDP()
                
            except:
                # do nothing
                pass
               
            if (int(round(time.time() * 1000)) - incomingDataTime)>1000:
                incomingDataTime = int(round(time.time() * 1000))
                self.receiveUDP()
            time.sleep(.01)


        if self.debugOutput:
                print("canO: Thread exit")
