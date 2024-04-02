#!/usr/bin/python

########################################################################
# V1.0
########################################################################

from smartBMS import Request, smartBMS
from CANtoProfinet import CANtoProfinet
from dataprocess import dataprocessing
import time
import threading
from multiprocessing import Queue




toBmsQueue = Queue()
fromBmsQueue = Queue()

toCANtoProfinet = Queue()
fromCANtoProfinet = Queue()



Starttime = int(round(time.time() * 1000))
if __name__ == '__main__':
    threads = []
    sendReq = 0

    bms = smartBMS(0,1000, toBmsQueue, fromBmsQueue)
    bms.start()

    CtP = CANtoProfinet(0, 1000, toCANtoProfinet, fromCANtoProfinet)
    CtP.start()
    
   
    dataproc = dataprocessing()

   
    time.sleep(.1)

    t = int(round(time.time() * 1000))
    updateTimeStart_dataprocessing = int(round(time.time() * 1000))
    
    try:
        while(1):
            
            
            try:
                qDatafromBMS = fromBmsQueue.get_nowait()
                if (qDatafromBMS):
                    #print(qDatafromBMS)
                    dataproc.updateBMS(qDatafromBMS)
                    print('BMS Daten geladen')
            except:
                # do nothing
                pass
            
            
   

            if (int(round(time.time() * 1000)) - updateTimeStart_dataprocessing) >250: # every 250ms   
                updateTimeStart_dataprocessing = int(round(time.time() * 1000))
                # jede x millisekunde werden die error codes und status bits neu berechnet
                
                
                BMS_Data = dataproc.getBMSdata()
                dataproc.printcodes()

                
                bms.printData()
                print('BMS Data: ',BMS_Data);
                Data = BMS_Data

                toCANtoProfinet.put(Data)
                
            


            time.sleep(.1)
    
        
    except KeyboardInterrupt:
        toBmsQueue.put("SIG-INT")
        toCANtoProfinet.put("SIG-INT")
   
        
        print("wait for threads to join")
        bms.join()
        CtP.join()
   
        print("threads successfully closed")
    


