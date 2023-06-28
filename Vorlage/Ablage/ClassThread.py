#!/usr/bin/python

########################################################################
# V 
########################################################################



import serial
import time
import threading
from multiprocessing import Queue

import logging


class UDPsr(threading.Thread):
    def __init__(self, inQueue, outQueue):
        threading.Thread.__init__(self)
        self.inQueue = inQueue
        self.outQueue = outQueue
        
    
    def sendedatenzurueck(self,var1):
        qDataOut={}
        spannung=10
        strom=20

        qDataOut ={'Spannung': spannung, 'Strom': strom}
        
        #Daten in out Que kopieren
        self.outQueue.put(qDataOut) 
        
     
        
    # Thread
    def run(self):
        self.running = True
        qDataIn={}
        
    
        while(self.running):
            time.sleep(.01)   #wichtig sonst 100% cpu auslastung
            
       
                #check for incoming data from main thread
            try:
                qDataIn = self.inQueue.get_nowait()

                if(qDataIn=="SIG-INT"):
                    # end thread
                    self.running = False
            except:
                # do nothing
                pass
            
            
            if qDataIn:
                print("QData")
                print(qDataIn)