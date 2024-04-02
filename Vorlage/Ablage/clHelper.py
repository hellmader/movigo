#!/usr/bin/python

########################################################################
# V1.0
########################################################################


import time

'''
from clHelper import checkTime
t1 = checkTime()
t2 = checkTime()

if( t2.getTime(60000) ):
        print("Script alle 60 Sekunden")
        
if( t1.getTime(30000) ):
        print("30Sec")
'''

class checkTime:
    #Non blocking sleep measurement - instead sleep function
    
    def __init__(self):
        self.lastNotifyTime = self.current_milli_time()
    
    def current_milli_time(self):
        return round(time.time() * 1000)
    
    
    
    def getTime(self, checkTime):
        if self.current_milli_time() - self.lastNotifyTime  > checkTime:
            self.lastNotifyTime =self.current_milli_time()
            flag = True
        else:
            flag=False
        
        return(flag)
            
         






