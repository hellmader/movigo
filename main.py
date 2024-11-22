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
import csv
import statistics  # To calculate mean values
UDP_IP = "192.168.10.112"  # IP address of the receiving Rock Pi 
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

soc = []
min_cell = []
max_cell = []
min_cell_array = []
max_cell_array = []
soc_array=[]

def add_to_limited_array(array, value, max_size=60):
    """
    Add a value to an array with a maximum size.
    If the array exceeds max_size, remove the oldest value.
    """
    array.append(value)  # Add the new value
    if len(array) > max_size:  # If size exceeds the limit
        array.pop(0)  # Remove the oldest value

def calculate_mean(array):
    """
    Calculate the mean of an array.
    The mean of 1 element is the element itself.
    """
    return statistics.mean(array) if array else 0  # Handles empty arrays gracefully
# Read the CSV file and populate the arrays
file_path = "newsoc.csv"  # Path to the uploaded file
try:
    with open(file_path, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')  # Use semicolon as the delimiter

        for row in reader:
            try:
                # Extract and clean values
                soc.append(float(row[0].strip('%').replace(',', '.')))  # Column 0: SoC
                min_cell.append(float(row[1].replace(',', '.')))       # Column 1: min cell
                max_cell.append(float(row[2].replace(',', '.')))       # Column 2: max cell
            except IndexError as e:
                print(f"Missing data in row: {row}, Error: {e}")
            except ValueError as e:
                print(f"Invalid data in row: {row}, Error: {e}")
    print(f"SoC array: {soc}")
    print(f"min_cell array: {min_cell}")
    print(f"max_cell array: {max_cell}")
except Exception as e:
    print(f"Error reading CSV file: {e}")

def get_soc(voltage, voltage_array, soc_array, mode='next_highest'):
    """
    Get the SoC value based on the voltage:
    - mode='next_highest': Get the next highest SoC (discharging).
    - mode='next_lowest': Get the next lowest SoC (charging).
    """
    if mode == 'next_highest':
        # Find the next highest SoC
        for i, v in enumerate(voltage_array):
            if voltage <= v:
                return soc_array[i]  # Return the next highest SoC
        return soc_array[-1]  # Default to 0% if below the lowest value
    elif mode == 'next_lowest':
        # Find the next lowest SoC
        for i in reversed(range(len(voltage_array))):
            if voltage >= voltage_array[i]:
                return soc_array[i]  # Return the next lowest SoC
        return 0  # Default to 0% if below the lowest value

    
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
    return(round(int(tempvalue)/1000,1))

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

            if (int(round(time.time() * 1000)) - updateTimeStart_dataprocessing) >1000:
                updateTimeStart_dataprocessing=int(round(time.time() * 1000))
                IO_Input = dataproc.getRequests()
                dataproc.calculateWarningCodes()
                warningA = dataproc.getWarningA()
                warningB = dataproc.getWarningB()
                dataproc.calculateErrorCodes()
                errorA = dataproc.getErrorA()
                errorB = dataproc.getErrorB()


                dataproc.shutdown_code()
                Data = dataproc.getBMSdata()
                if (Data['maximale Zellspannung']!=5):
                    Data.update({'WarningA': warningA,  'WarningB': warningB, 'ErrorA':errorA, 'ErrorB':errorB})
                    Data.update(IO_Input)
                    #Data.update(ueberwache_system())
                    Data.update({'Zeit': TimeStmp()})
                    DataUDP=({'Voltage': Data['Spannung']})
                    DataUDP.update({'Current': Data['Strom']})
                    #DataUDP.update({'SoC': Data['SoC']})
                    DataUDP.update({'Temp1': Data['Temperatur 1']})
                    DataUDP.update({'Temp2': Data['Temperatur 2']})
                    DataUDP.update({'Temp3': Data['Temperatur 3']})
                    DataUDP.update({'CPUTemp': CPUTemp})
                    #DataUDP.update({'min CellVoltage': Data['minimale Zellspannung']})
                    #DataUDP.update({'max CellVoltage': Data['maximale Zellspannung']})
 
                    
                    min_cell_voltage = Data['minimale Zellspannung']
                    max_cell_voltage = Data['maximale Zellspannung']
                    add_to_limited_array(min_cell_array, min_cell_voltage)  # Update min_cell_array
                    add_to_limited_array(max_cell_array, max_cell_voltage)  # Update max_cell_array
                    # Calculate mean values of the arrays
                    min_cell_mean = round(calculate_mean(min_cell_array), 4)  # Round to 2 decimals
                    max_cell_mean = round(calculate_mean(max_cell_array), 4)  # Round to 2 decimals
                    
                    current = Data['Strom']
                    # Update Data and DataUDP with the mean values
                    DataUDP.update({'Mean Min Cell Voltage': min_cell_mean, 'Mean Max Cell Voltage': max_cell_mean})
                    try:
                        if current < 0:  # Discharging
                            #print("mincellstat")
                            new_soc = get_soc(min_cell_mean, min_cell, soc, mode='next_lowest')
                        else:  # Charging
                            #print("maxcellstat")
                            new_soc = get_soc(max_cell_mean, max_cell, soc, mode='next_highest')
                        #print(new_soc)   
                        add_to_limited_array(soc_array, new_soc)
                        new_soc = round(calculate_mean(soc_array), 0)
                        # Update SoC in Data
                        #Data['SoC'] = new_soc
                        DataUDP.update({'SoC': new_soc})  # Update in UDP data as well
                        DataUDP.update({'Time': Data['Zeit']})
                    except ValueError as e:
                        print(f"Error in SoC calculation: {e}")
                        Data['SoC'] = None  # Fallback if calculation fails
                    try:
               
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
