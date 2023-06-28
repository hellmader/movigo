# -*- coding: utf-8 -*-
"""
Created on Fri Jun  3 07:19:46 2022

@author: produktion
"""



from ClassThreadV1 import UDP
import threading
from multiprocessing import Queue
import time

toUDPQueue = Queue()
fromUDPQueue = Queue()

i=0

if __name__ == '__main__':
    
    UDP = UDP(0,1000,toUDPQueue, fromUDPQueue)
    UDP.start()
    
    updateTimeStart = int(round(time.time() * 1000))
    
    try:
        while(1):
            try:
                qfromUDP = fromUDPQueue.get_nowait()
                print('Data from UDP:   ',qfromUDP)

            except:
                pass
            if (int(round(time.time() * 1000)) - updateTimeStart) >3000: # every 5000ms 
                updateTimeStart = int(round(time.time() * 1000))
                i=i+1
                toUDPQueue.put(i)
            time.sleep(0.01)

    except KeyboardInterrupt:
        toUDPQueue.put("SIG-INT")
        
        print("wait for threads to join")
        UDP.join()

        print("threads successfully closed")
    