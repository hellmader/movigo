#!/usr/bin/python3
import socket
import json
import time
from clBMS import Request, smartBMS
from dataprocess import dataprocessing
import threading
from threading import Thread
from multiprocessing import Queue
import configparser
from psutils import ueberwache_system
import requests
from clTBH import clTBH
import subprocess
import signal
from datetime import datetime
from clHelper import checkTime


UDP_IP = "192.168.89.1"  # IP address of the receiving Rock Pi 
UDP_PORT = 5005
threads = []
config = configparser.ConfigParser()
config.read("/home/hell/sw/etc/bms.config")

counter = 0
toBmsQueue = Queue()
fromBmsQueue = Queue()

threads = []

bms = smartBMS(0,1000, toBmsQueue, fromBmsQueue)
bms.start()

dataproc = dataprocessing()
Data = {}
counterthb=0
sock=None
time.sleep(.1)
updateTimeStart_dataprocessing = int(round(time.time() * 1000))
def TimeStmp():
    #date and time
    Zeit = datetime.now()
    dt_string = Zeit.strftime("%d.%m.%Y %H:%M:%S")
    return(dt_string)

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

if __name__ == '__main__':    
    try:
        t2 = checkTime()
        CPUTemp= rTemp(temp_base)
        while True:
            time.sleep(0.1)
            try:
                qDatafromBMS = fromBmsQueue.get_nowait()
                if qDatafromBMS:
                    time_stamp = time.time()
                    dataproc.updateBMS(qDatafromBMS)
                    qDatafromBMS_prev = qDatafromBMS
                else:
                    if time.time() - time_stamp >= 5:
                        dataproc.calculateStatusCodes(IO_Output,1)

                    dataproc.updateBMS(qDatafromBMS_prev)

            except: 
                pass

                #Temperatur sensor Rock PI E auslesen
            if( t2.getTime(60000) ):
                CPUTemp= rTemp(temp_base)

            if (int(round(time.time() * 1000)) - updateTimeStart_dataprocessing) >250:
                counter+=1
                IO_Input = dataproc.getRequests()
                dataproc.calculateWarningCodes()
                warningA = dataproc.getWarningA()
                warningB = dataproc.getWarningB()
                dataproc.calculateErrorCodes()
                errorA = dataproc.getErrorA()
                errorB = dataproc.getErrorB()


                dataproc.shutdown_code()
                Data = dataproc.getBMSdata()
                Data.update({'WarningA': warningA,  'WarningB': warningB, 'ErrorA':errorA, 'ErrorB':errorB})
                Data.update(IO_Input)
                #Data.update(ueberwache_system())
                Data.update({'Zeit': TimeStmp()})
                DataUDP=({'Voltage': Data['Spannung']})
                DataUDP.update({'Current': Data['Strom']})
                DataUDP.update({'SoC': Data['SoC']})
                DataUDP.update({'Temp1': Data['Temperatur 1']})
                DataUDP.update({'Temp2': Data['Temperatur 2']})
                DataUDP.update({'Temp3': Data['Temperatur 3']})
                DataUDP.update({'CPUTemp': CPUTemp})
                DataUDP.update({'min CellVoltage': Data['minimale Zellspannung']})
                DataUDP.update({'max CellVoltage': Data['maximale Zellspannung']})
                DataUDP.update({'Time': Data['Zeit']})
                if counter==9:
                    try:
                        counter=0
                        if sock==None:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
                            message_to_send = json.dumps(DataUDP).encode()  # convert the dictionary to a JSON string and then to bytes
                            sock.sendto(message_to_send, (UDP_IP, UDP_PORT))
                    except:
                        pass






    except KeyboardInterrupt:
        toBmsQueue.put("SIG-INT")  
        toTBHQueue.put("SIG-INT")
        bms.join()
        os.killpg(os.getpgid(process.pid),signal.SIGTERM)
        os.systemc('sudo systemctl stop profinet')
        bms.join()
        tb.join()        
        print("threads successfully closed")
