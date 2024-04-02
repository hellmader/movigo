#!/usr/bin/python

########################################################################
# V1.0
########################################################################


from smartBMS import Request, smartBMS
from dataprocess import dataprocessing
import time
import threading
from multiprocessing import Queue
from clHelper import checkTime
from clTBH import clTBH
import configparser
import logging

config = configparser.ConfigParser()
config.read("/home/hell/sw/etc/bms.config")


TBServer  = config['thingsboard']['Server']
TBToken  = config['thingsboard']['Token']
TBAkku  = config['thingsboard']['Akku']

logger = logging.getLogger()
logger.setLevel(logging.ERROR)   



toBmsQueue = Queue()
fromBmsQueue = Queue()
toTBHQueue = Queue()

qDatafromBMS = 0
Data={}




Starttime = int(round(time.time() * 1000))
if __name__ == '__main__':
    threads = []
    sendReq = 0
    
    t1 = checkTime()  

    bms = smartBMS(0,1000, toBmsQueue, fromBmsQueue)
    bms.start()


    tb = clTBH(toTBHQueue, host=TBServer, token=TBToken, port=1883  )   # thingsboard connection
    tb.start()
    
    dataproc = dataprocessing()


    time.sleep(.1)

    t = int(round(time.time() * 1000))
    updateTimeStart_dataprocessing = int(round(time.time() * 1000))
    updateTimeStart_thingsboard = int(round(time.time() * 1000))
    
    try:
        while(1):
            
            
            try:
                qDatafromBMS = fromBmsQueue.get_nowait()
                if (qDatafromBMS):
                    #print(qDatafromBMS)
                    dataproc.updateBMS(qDatafromBMS)
                    #print('BMS Daten geladen')
            except:
                # do nothing
                pass
            

            if (int(round(time.time() * 1000)) - updateTimeStart_dataprocessing) >250: # every 250ms   
                updateTimeStart_dataprocessing = int(round(time.time() * 1000))
                # jede x millisekunde werden die error codes und status bits neu berechnet
                
                
                BMS_Data = dataproc.getBMSdata()
                #print('BMS Data: ',BMS_Data)
                Data=BMS_Data
            

            
                
            #Daten an Thingsboard senden
            if( t1.getTime(5000) ):

                Data.update({'Akkuname': TBAkku})
                toTBHQueue.put(Data) 
                print("Thingsboard upload")
                



            time.sleep(.1)
    
        
    except KeyboardInterrupt:
        toBmsQueue.put("SIG-INT")
        
        print("wait for threads to join")
        bms.join()
        print("threads successfully closed")
    


