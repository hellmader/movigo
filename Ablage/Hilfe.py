#!/usr/bin/python

########################################################################
# V1.0
########################################################################


'''
#### Abfrage 'IOs

from clIO import clIO
import time
from multiprocessing import Queue
import threading

fromclIOtomain = Queue()
toclIOfrommain = Queue()


Update = int(round(time.time() * 1000))
Flag = False
data1 = {'Status_AUX1':1, 'Request_AUX2':0,'Request_P':0, 'Request_C':0, 'Request_sleep':0}
data2 = {'Status_AUX1':0, 'Request_AUX2':1,'Request_P':0, 'Request_C':0, 'Request_sleep':0}

if __name__ == '__main__':
    threads = []
    sendReq = 0

    clIO = clIO(0, 1000, fromclIOtomain, toclIOfrommain)
    clIO.start()
    time.sleep(1)
    try:
        while(1):
                        
            try:
                qData_fromclIO = fromclIOtomain.get_nowait()
                print(qData_fromclIO)    
                    
                
            except:
                # do nothing
                pass
            if ((time.time() - Update)>5) and (Flag == False):
                Update = time.time()
                Flag = True
                toclIOfrommain.put(data1)
                
            if ((time.time() - Update)>5) and (Flag == False):
                Update = time.time()
                Flag = False
                toclIOfrommain.put(data2)
    
    except KeyboardInterrupt:
        toclIOfrommain.put("SIG-INT")
       
        print("wait for threads to join")
        clIO.join()

        print("threads successfully closed")                



print('Test beendet')

'''
### abfrage Ladegerät
from programm_Ladegeraet import Ladegeraet
from multiprocessing import Queue
import threading
import time

fromLadegeraet = Queue()
toLadegeraet = Queue()


Update = int(round(time.time() * 1000))

if __name__ == '__main__':
    threads = []
    sendReq = 0

    lade = Ladegeraet(0, 1000, fromLadegeraet, toLadegeraet)
    lade.start()
    time.sleep(1)
    Update = int(round(time.time() * 1000))
    updateTimeStart_dataprocessing = int(round(time.time() * 1000))
    Regler=1
    SoC = 50 
    try:
        
        while(Update <30*1000):
            '''
            try:
                qData_toCANfromLadegeraet = fromLadegeraet.get_nowait()
                print(qData_toCANfromLadegeraet)    
                
                
            except:
                # do nothing
                pass
            #print((int(round(time.time() * 1000)) - Update >10*1000)and(int(round(time.time() * 1000)) - Update <20*1000))
            '''
            if (int(round(time.time() * 1000)) - updateTimeStart_dataprocessing) >1000: # every 250ms   
                updateTimeStart_dataprocessing = int(round(time.time() * 1000))
                if (int(round(time.time() * 1000)) - Update >10*1000)and(int(round(time.time() * 1000)) - Update <20*1000):
                    Regler=0
                    SoC = 0
                    if SoC==0:
                        SoC=1
                    print('Hallllo')
                    data = {'SoC':SoC,'Regler':Regler}


                if (int(round(time.time() * 1000)) - Update >20*1000)and (int(round(time.time() * 1000)) - Update <24*1000):
                    Regler = 1
                    print('Wellllllllllt')
                    data = {'SoC':SoC,'Regler':Regler}

                    if (int(round(time.time() * 1000)) - Update >22*1000):
                        Regler = 0
                    print('Laden beendet')
                print(data)
                toLadegeraet.put(data)

    except KeyboardInterrupt:
        toLadegeraet.put("SIG-INT")

        
        print("wait for threads to join")
        lade.join()
        print("threads successfully closed")


'''
####Abfrage BMS
from smartBMS import Request, smartBMS
import time
import threading
from multiprocessing import Queue


toBmsQueue = Queue()
fromBmsQueue = Queue()

if __name__ == '__main__':
    threads = []
    sendReq = 0

    bms = smartBMS(0,1000, toBmsQueue, fromBmsQueue)
    bms.start()


    time.sleep(.1)

    
    try:
        while(1):
            
            
            try:
                qDatafromBMS = fromBmsQueue.get_nowait()
                if (qDatafromBMS):
                    print(qDatafromBMS)
                    print('BMS Daten geladen')
                
            except:
                # do nothing
                pass

            time.sleep(.1)
    
        
    except KeyboardInterrupt:
        toBmsQueue.put("SIG-INT")

        
        print("wait for threads to join")
        bms.join()
        print("threads successfully closed")
'''  


###Abfrage Klasse dataprocessing



