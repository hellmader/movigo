#!/usr/bin/python

########################################################################
# V1.0
########################################################################

from cl_testsmartBMS import Request, smartBMS
import time
import threading
from multiprocessing import Queue
from clHelper import checkTime


toBmsQueue = Queue()
fromBmsQueue = Queue()
qDatafromBMS=[]


Starttime = int(round(time.time() * 1000))
if __name__ == '__main__':
   
    t1 = checkTime()

    bms = smartBMS(0,1000, toBmsQueue, fromBmsQueue)
    bms.start()


    try:
        while(1):
            
            time.sleep(.1)     # ohne sleep 120% cpu auslastung 
                                # mit .01 2%
                                # mit .1  1% oder kleiner
                                
                                #Prozesse| Threads prüfen
                                # ps -eaf | grep test-bms
                                # top -H -p <pid>
                                # ps  -afT -p <pid>   
                                
                                #htop graphische process textanzeige
            try:
                qDatafromBMS = fromBmsQueue.get_nowait()
               
            except:
                # do nothing
                pass
            
            
            
            if t1.getTime(1000):
                if (qDatafromBMS):
                    pass
                    print(qDatafromBMS) 
                    print(" ")
                    print("  ")
                else:
                    pass
                    print("no Bms data")
           
        
    except KeyboardInterrupt:
        toBmsQueue.put("SIG-INT")
        
        print("wait for threads to join")
        bms.join()
        print("threads successfully closed")
    


