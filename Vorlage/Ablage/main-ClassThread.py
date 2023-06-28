

from ClassThread import UDPsr
import threading
from multiprocessing import Queue
from clHelper import checkTime
import time

toUDPsrQueue = Queue()
fromUDPsrQueue = Queue()


while True:
    
    udpsr = UDPsr(toUDPsrQueue, fromUDPsrQueue)
    udpsr.start()
    
    
    t1 = checkTime()  
    
    
    if( t1.getTime(1000) ):
        toQueue={}
        spannung=10
        strom=20
        print("send Data")
        
        toQueue = {'Spannung': spannung, 'Strom': strom}
        toUDPsrQueue.put(toQueue)