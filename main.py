#!/usr/bin/python3

########################################################################
# V1.0
########################################################################


#from re import S
tcpdump_logg=False
csv_logg=False
candump_logg=False

import pprint
from clBMS import Request, smartBMS
from dataprocess import dataprocessing

import time
from datetime import datetime
import threading
from multiprocessing import Queue
from programm_Ladegeraet import Ladegeraet
from clIO import clIO
import configparser
import logging
from clHelper import checkTime
from clTBH import clTBH
import os
from write_csv import write_csv
import psutil
from psutils import ueberwache_system
import os
import requests
import pandas as pd
import time, sys
import tcpfile
import canfile
from threading import Thread


config = configparser.ConfigParser()
config.read("/home/hell/sw/etc/bms.config")

#Logging aktivieren/deaktivieren
if tcpdump_logg:
    import subprocess
    import signal

TBServer  = config['thingsboard']['Server']
TBToken  = config['thingsboard']['Token']
TBAkku  = config['thingsboard']['Akku']
TBSN  = config['thingsboard']['Seriennummer']
APP_Mode=TBSN[:4]

TuenkersPROFI_ID=["3042","3419"]
TuenkersCAN_ID=["3212","3222","2455","3470"]
if APP_Mode in(TuenkersPROFI_ID):
    from UDP_p import UDP
    APP_Mode = "TuenkersPROFI"
elif APP_Mode in(TuenkersCAN_ID):
    from UDP_c import UDP
    APP_Mode = "TuenkersCAN"


#logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.INFO)           #Testausgabe Werte
#logging.basicConfig(level=logging.WARNING)
#logging.basicConfig(level=logging.ERROR)   

LevelState=logging.ERROR
#LevelState=logging.INFO
logging.basicConfig(level=LevelState)   

toBmsQueue = Queue()
fromBmsQueue = Queue()

fromLadegeraet = Queue()
toLadegeraet = Queue()

toUDPQueue = Queue()
fromUDPQueue = Queue()

toTBHQueue = Queue()

qDatafromBMS = 0
Data={}
tocsv = Queue()
cpu_max=0.0

# read Rock Pi CPU Temperatur sensor
temp_base ="/sys/class/thermal/thermal_zone0/temp"

def rTemp(tempsensor):
  try:
    f = open(tempsensor,'r')
    tempvalue=f.readline()
    f.close
  except:
    tempvalue=0
  
  #print("CPUTemp:", tempvalue)

  return(tempvalue)

def TimeStmp():
  #date and time
  Zeit = datetime.now()
  dt_string = Zeit.strftime("%d.%m.%Y %H:%M:%S")
  return(dt_string)


Starttime = int(round(time.time() * 1000))
if __name__ == '__main__':
    
    logging.error("Programm Start...")
    threads = []
    sendReq = 0
    
    
    
    t1 = checkTime()  
    t2 = checkTime()  
    t3 = checkTime()
    #Threads starten
    bms = smartBMS(0,1000, toBmsQueue, fromBmsQueue)
    bms.start()
    
    lade = Ladegeraet(0, 1000, fromLadegeraet, toLadegeraet)
    lade.start()

    UDP = UDP(0,1000,toUDPQueue, fromUDPQueue)
    UDP.start()

    tb = clTBH(toTBHQueue, host=TBServer, token=TBToken, port=1883  )  # Thingsboard connection
    tb.start()
    
    if csv_logg:
        tc = write_csv(0,1000,tocsv)
        tc.start()
    
    dataproc = dataprocessing()
    
    io = clIO()

    time.sleep(.1)

    t = int(round(time.time() * 1000))
    updateTimeStart_dataprocessing = int(round(time.time() * 1000))
    updateTimeStart_Ladegeraet = int(round(time.time() * 1000))
    updateTimeStart_Ladegeraet_laden = int(round(time.time() * 1000))
    updateTimeStart_ChargeRate = int(round(time.time() * 1000))
    Timer_Ladegeraet_present = 0
    Flag = False
    
    time_stamp = 0
    time_start = time.time()
    timecheck=time_start
    #tcpdump
    if tcpdump_logg:
       tcpfile_thread = Thread(target=tcpfile.main)
       tcpfile_thread.start()
    #candump  
    if candump_logg:
       canfile_thread = Thread(target=canfile.main)
       canfile_thread.start()
    
    try:
        while(1):
            timecheck=time.time()
            time_start = time.time()
            testzeit=0
            time.sleep(.01)   #wichtig sonst 100% cpu auslastung


                    
                
            try:
                qDatafromBMS = fromBmsQueue.get_nowait()
                if (qDatafromBMS):
                    time_stamp = time.time()
                    dataproc.updateBMS(qDatafromBMS)
                    qDatafromBMS_prev = qDatafromBMS
                else:
                    #wenn BMS-TimeOut, dann Wert von vorher übernehmen
                    if time.time() - time_stamp >= 5:
                        dataproc.calculateStatusCodes(IO_Output,1)
                        
                    dataproc.updateBMS(qDatafromBMS_prev)

            except:
                # do nothing
                pass
            
            try:
                qfromUDP = fromUDPQueue.get_nowait()
                qfromUDP.update({'APP_Mode': APP_Mode})
                dataproc.DatafromProfinet(qfromUDP)
                
            except:
                pass
                
            try:
                qData_fromLadegeraet = fromLadegeraet.get_nowait()
                dataproc.UpdateCANfromLadegeraet(qData_fromLadegeraet)
                logging.info('Nachricht von Ladegerät erhalten')
            except:
                # do nothing
                pass
            
                
            if (int(round(time.time() * 1000)) - updateTimeStart_dataprocessing) >250: # every 250ms   
                updateTimeStart_dataprocessing = int(round(time.time() * 1000))
                
                #setzen der Relais
                IO_Input = dataproc.getRequests()
                IO_Input.update({'TBSN': TBSN,'APP_Mode': APP_Mode})
                relay_error = io.IO_set_and_check(IO_Input)
                logging.info(relay_error)
                dataproc.Status_Relais_F(relay_error)
                
                #error codes und status bits neu berechnet
                BMS_Data = dataproc.getBMSdata()
                IO_Output = io.StatusIOs()
                dataproc.calculateStatusCodes(IO_Output)
                statusA = dataproc.getStatusA()
                statusB = dataproc.getStatusB()
                dataproc.calculateWarningCodes()
                warningA = dataproc.getWarningA()
                warningB = dataproc.getWarningB()
                dataproc.calculateErrorCodes()
                errorA = dataproc.getErrorA()
                errorB = dataproc.getErrorB()
                

                dataproc.shutdown_code()
                
                Data = BMS_Data
                Data.update({'StatusA': statusA, 'StatusB': statusB, 'WarningA': warningA,  'WarningB': warningB, 'ErrorA':errorA, 'ErrorB':errorB})
                Data.update(IO_Input)
                
                Data.update({'APP_Mode': APP_Mode})
                Data.update(ueberwache_system())
                CPUTemp= ueberwache_system()["CPUTemp"]
                #print(CPUTemp)
                #dataproc.printcodes()
                if APP_Mode in("TuenkersCAN" ,"TuenkersPROFI"):
                    dataproc.Ladegeraet_present()
                    dataproc.Ladegeraet_aktiv()
                    dataproc.Ladevorgang_beendet()
                    if APP_Mode in("TuenkersPROFI"):
                        Data.update({'tcharge': dataproc.getChargeRate()})
                    Data.update({'StatusLaden': dataproc.Status_laden_bereit()})
                    Data.update({'StatusLadenEnde': dataproc.Status_laden_beendet()})


                lade.writeLadegeraet(Data)
                Data.update({'Zeit': TimeStmp()  })
                toLadegeraet.put(Data)
                toTBHQueue.put(Data)
                #Daten an csv
                if csv_logg:
                    tocsv.put(Data)
                toUDPQueue.put(Data)
                


    
        
    except KeyboardInterrupt:
        toBmsQueue.put("SIG-INT")
        toLadegeraet.put("SIG-INT")
        toTBHQueue.put("SIG-INT")
        toUDPQueue.put("SIG-INT")
        toTBHQueue.put("SIG-INT")
        os.killpg(os.getpgid(process.pid),signal.SIGTERM)
        os.systemc('sudo systemctl stop profinet')
        
        print("wait for threads to join")
        bms.join()
        lade.join()
        UDP.join()
        tb.join()        
        print("threads successfully closed")
    


