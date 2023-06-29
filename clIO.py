#!/usr/bin/python

########################################################################
# V1.0
########################################################################

# https://learn.adafruit.com/mcp230xx-gpio-expander-on-the-raspberry-pi?view=all
# https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/tree/legacy

# bei aufruf der Configuration für den mcp23008 werden die relais geschalten
"""
Created on Sat Mar 19 10:42:34 2022

@author: MichaelMader
Quelle:
    https://wiki.52pi.com/index.php?title=EP-0099
"""

'''

from clIO import clIO
import time as t

io = clIO()
#io.Demo()  #schaltet alle 4 Relais aus und ein

print Relais nr1 einschalten
io.SetRelay(1,0)    #Relais Nr, ON 1, Off 0
t.sleep(1)

print("Status Relais:")
print("1:",  io.GetRelay(1) )
      
'''

import time as t
import smbus
import sys
from Adafruit_I2C import Adafruit_I2C
from MCP230xx import Adafruit_MCP230XX as MCP230xx


class clIO:

    def __init__(self,DEVICE_BUS = 1, DEVICE_ADDR = 0x20):
        self.DEVICE_BUS = DEVICE_BUS
        self.DEVICE_ADDR = DEVICE_ADDR
        
        #Relais
        self.bus = smbus.SMBus(DEVICE_BUS)
        self.mcp = MCP230xx(busnum = DEVICE_BUS, address = 0x20, num_gpios = 8) 
            
        
        #Pin definition für relay überwachung
        #self.mcp.pinMode(8, self.mcp.INPUT)	#GPB8
        #self.mcp.pullUp(8, 1)		#Pullup enable


        self.mcp.config(0, self.mcp.OUTPUT) #output dcdc enable 
        self.mcp.pullup(0,0) 

        self.mcp.config(1, self.mcp.OUTPUT)   # 1 ... OUTPUT 24V relais AUX2
        self.mcp.pullup(1,0)

        self.mcp.config(2, self.mcp.OUTPUT)   # 1 ... OUTPUT 48V Relais Entladen
        self.mcp.pullup(2,0)

        self.mcp.config(3,self.mcp.OUTPUT)   # 1 ... OUTPUT 48V relais Laden
        self.mcp.pullup(3,0) 


        self.mcp.config(4,self.mcp.INPUT)   # 1 ... INPUT dcdc enable 24v check
        self.mcp.pullup(4,0)

        self.mcp.config(5,self.mcp.INPUT)   # 1 ... INPUT 24V Relais AUX2 check
        self.mcp.pullup(5,0)

        self.mcp.config(6,self.mcp.INPUT)   # 1 ... INPUT Entladen 48V Check
        self.mcp.pullup(6,0)

        self.mcp.config(7,self.mcp.INPUT)   # 1 ... INPUT laden 48V check
        self.mcp.pullup(7,0)



        self.Status_AUX1=1
        self.Request_AUX2 = 0
        self.Request_P = 0
        self.Request_C = 0
        self.Request_sleep = 0
        self.Relais_error = 1
        self.Starttime = int(round(t.time() * 1000))
        self.Flag_Relay_C=False
        self.Zahl = 0
    
    def SetRelay(self,RELnr, OnOff):
      if RELnr == 1:
        self.mcp.output(0,OnOff)

      if RELnr == 2:
        self.mcp.output(1,OnOff)
            
      if RELnr == 3:
        self.mcp.output(2,OnOff)

      if RELnr == 4:
        self.mcp.output(3,OnOff)
        
        #prüfen ob relais eingeschaltet hat
        #return(self.GetRelay(RELnr) )
            
    
    #0 Relais ausgeschaltet
    #1 Relais eingeschaltet
    def GetRelay(self,RELnr):
        #t.sleep(0.1)
        if RELnr == 1:  #24V DCDC enabled
            ReturnInput=self.mcp.input(4)

        if RELnr == 2:  #24V REL AUX2
            ReturnInput=self.mcp.input(5)

        if RELnr == 3: #48V Entladen
            ReturnInput=self.mcp.input(6)

        if RELnr == 4: #48V Laden
            ReturnInput=self.mcp.input(7)

        
        return(ReturnInput)            
    
    def IO_set_and_check(self, data):
        if data != None:
            self.Status_AUX1 = data['Status_AUX1']
            self.Request_AUX2 = data['Request_AUX2']
            self.Request_P = data['Request_P']
            self.Request_C = data['Request_C']
            self.Request_sleep = data['Request_sleep']
        
        if self.Request_sleep == 0:
            pass
        else:
            self.Status_AUX1 = 0
            self.Request_AUX2 = 0
            self.Request_AUX3 = 0
            self.Request_AUX4 = 0
            self.Request_P = 0
            self.Request_C = 0
            self.Request_sleep = 1
        
        if data['APP_Mode'] == 'TuenkersPROFI':
            self.Request_AUX2 = 1
            if self.Request_sleep == 0:
                pass
            else:
                self.Status_A0_AUX1 = 1
                self.Request_AUX2 = 0
            if self.Status_AUX1 == 0:
                #t.sleep(2)
                self.SetRelay(1, 0)
            else:
                self.SetRelay(1, 1)
                
            if data['TBSN'][4:6] == '-1':
                if self.Request_AUX2 == 0:
                    #t.sleep(2)
                    self.SetRelay(2, 1)
                else:
                    self.SetRelay(2, 0)
            else:
                if self.Request_AUX2 == 0:
                    #t.sleep(2)
                    self.SetRelay(2, 0)
                else:
                    self.SetRelay(2, 1)
        
            if self.Request_P == 0:
                #t.sleep(2)
                self.SetRelay(3, 0)
            else:
                self.SetRelay(3, 1)
                
            if self.Request_C == 0:
                if self.Flag_Relay_C ==True:
                    if (int(round(t.time() * 1000)) - self.Starttime) >250: # every 250ms   
                        self.Starttime = int(round(t.time() * 1000))
                        self.Zahl = self.Zahl +1
                        if self.Zahl >= 12:
                            self.SetRelay(4, 0)
                            self.Flag_Relay_C = False
                            self.Zahl = 0
                            
            else:
                self.SetRelay(4, 1)
                self.Flag_Relay_C = True
        
        if data['APP_Mode'] == 'TuenkersCAN':
            if data['TBSN'][4:6] in ('-1','-2','-3','-4','-5','-6'):
                if self.Status_AUX1 == 0:
                    #t.sleep(2)
                    self.SetRelay(1, 1)
                else:
                    self.SetRelay(1, 0)
            else:
                if self.Status_AUX1 == 0:
                    #t.sleep(2)
                    self.SetRelay(1, 0)
                else:
                    self.SetRelay(1, 1)
            
            if self.Request_AUX2 == 0:
                #t.sleep(2)
                self.SetRelay(2, 0)
            else:
                self.SetRelay(2, 1)
            if self.Request_P == 1 and self.Request_C == 1:
                self.SetRelay(3, 1)
                self.Flag_Relay_C = True
            elif self.Request_P == 1 and self.Request_C == 0:
                self.SetRelay(3, 1)
                self.Flag_Relay_C = False
            elif self.Request_P == 0 and self.Request_C == 1:
                self.SetRelay(3, 1)
                self.Flag_Relay_C = True
            else:
                if self.Flag_Relay_C ==True:
                    if (int(round(t.time() * 1000)) - self.Starttime) >250: # every 250ms   
                        self.Starttime = int(round(t.time() * 1000))
                        self.Zahl = self.Zahl +1
                        if self.Zahl >= 12:
                            self.SetRelay(3, 0)
                            self.Flag_Relay_C = False
                            self.Zahl = 0
                else: 
                    self.SetRelay(3, 0)

            
            
        t.sleep(0.05)
        
        if (self.Status_AUX1 == self.GetRelay(1)) and (self.Request_AUX2 == self.GetRelay(2)) and (self.Request_P == self.GetRelay(3)) and (self.Request_C == self.GetRelay(4)):
            self.Relais_error = {'Relais_error':0}
        else:
            self.Relais_error = {'Relais_error':1}

        return self.Relais_error
        
    def printIOs(self):
        print('Status_AUX1',self.Status_AUX1)
        print('Request_AUX2',self.Request_AUX2)
        print('Request_P',self.Request_P)
        print('Request_C',self.Request_C)
        print('Request_sleep',self.Request_sleep)

    def StatusIOs(self):
        #Status_relais = {'Status_AUX1':self.GetRelay(1),'Status_AUX2':self.Request_AUX2, 'Status_P':self.GetRelay(3), 'Status_C':self.GetRelay(4)}
        Status_relais = {'Status_AUX1':self.Status_AUX1,'Status_AUX2':self.Request_AUX2, 'Status_P':self.Request_P, 'Status_C':self.Request_C}
        return Status_relais
            
    
'''
    def Demo(self):
        while True:
            try:
                for i in range(1,5):
                    self.bus.write_byte_data(self.DEVICE_ADDR, i, 0xFF)
                    print("Relais Nr: {}".format(i-1) )
                    t.sleep(3)
                    self.bus.write_byte_data(self.DEVICE_ADDR, i, 0x00)
                    t.sleep(3) 
            except KeyboardInterrupt as e:
                print("Quit the Loop")
                sys.exit()
'''
