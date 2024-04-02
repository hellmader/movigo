#!/usr/bin/python

########################################################################
# V1.0
########################################################################

#https://github.com/thingsboard/thingsboard-python-client-sdk/blob/master/tb_device_mqtt.py
#https://thingsboard.io/docs/pe/reference/python-client-sdk/



import time
import threading
from multiprocessing import Queue
from clHelper import checkTime
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
import logging



class clTBH(threading.Thread):
    def __init__(self, inQueue,  host, token, port=1883  ):
        threading.Thread.__init__(self)
        self.inQueue = inQueue
        self.host = host
        self.token = token
        self.port=port
        self.t1 = checkTime()   
        self.DataAccept = False

     
        
    def run(self):
        self.running = True

        self.client =  TBDeviceMqttClient( self.host, self.token, self.port )
        
        while(self.running):
            time.sleep(.01)   #wichtig sonst 100% cpu auslastung

            
            if self.client.is_connected() == False:
              try:
                #print("start Verbindungsaufbau ...")
                self.client.connect()
                #print("Verbindungsaufbau erfolgreich")
                time.sleep(2)

              except:
                #print("Verbindungsaufbau fehler")
                time.sleep(2)




 
            #check for incoming queue data from main thread
            try:
                qDataIn = self.inQueue.get_nowait()
                if(qDataIn=="SIG-INT"):
                    # end thread
                    self.running = False

                self.DataAccept = True  # Flag für Daten bekommen, get_nowait erzeugt einen fehler wenn keine daten kommen
                                        # dadurch wird dieses Flag/Zeile nicht erreicht sonder die exception ausgelöst
            except:
                self.DataAccept = False
                pass
            
          
            try:
                if  self.DataAccept:
                    self.DataAccept = False

                    #print("DATA:::") 
                    #print(qDataIn)    
                    self.client.send_telemetry(qDataIn)
            
            except:
                pass
            

        
