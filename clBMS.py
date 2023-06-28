#!/usr/bin/python

########################################################################
# V1.0
########################################################################

# https://blog.ja-ke.tech/2020/02/07/ltt-power-bms-chinese-protocol.html#

import serial
import time
import threading
from multiprocessing import Queue
import enum
import logging


class Request(enum.Enum):
    NONE = 0
    BASIC_INFO = 1
    CELL_VOLTAGE = 2


def current_milli_time():
    return round(time.time() * 1000)

class smartBMS(threading.Thread):
    def __init__(self, debugOutput, updateCycle, inBmsQueue, outBmsQueue):
        threading.Thread.__init__(self)
        self.debugOutput = debugOutput
        self.updateCycle = updateCycle
        self.inBmsQueue = inBmsQueue
        self.outBmsQueue = outBmsQueue
        self.bmsState   = Request.NONE
        self.requestTimout  = 500
        self.lastrequest = 0
        if self.debugOutput:
            print("smartBMS: Init - Debug enabled")
        # open serial port
        if self.debugOutput:
            print("smartBMS: Init - Open Seiral Port")
        self.serialBMS = serial.Serial()
        self.serialBMS.baudrate = 9600
        #self.serialBMS.port = '/dev/ttyUSB1'
        #self.serialBMS.port = '/dev/ttyAMA0'
        self.serialBMS.port = '/dev/ttyS2'
        self.serialBMS.timeout = 0.2
        self.serialBMS.open()
        #self.can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan_ctypes')# socketcan_native
        self.lastNotifyTime = current_milli_time()
        # basic info
        self.total_voltage = 0
        self.current = 0
        self.residual_capacity_ = 0
        self.nominal_capacity_ = 0
        self.cycle_life_ = 0
        self.product_data_ = 0
        self.balance_status_low_ = 0
        self.balance_status_high_ = 0
        self.protection_status_ = 0
        self.version_info_ = 0
        self.rsoc = 0
        self.fet_controll_status = 0
        self.cell_block_serie = 0
        self.last_updateBasicInfo = 0
        self.NTC_sensor_numbers = 0
        self.sensor_values = []
        #cell voltage
        self.cellVoltages = []
        self.last_updateCellVoltages = 0
        #bmsversion
        self.bmsversion = ""
        

    def calcChecksum(self, data):
        tmp = 0
        for x in data:
            tmp = tmp + x
        tmp ^= 0xffff
        tmp += 1
        return tmp

    def calcIncChecksum(self, data):
        sum = 0
        for x in data:
            #sum = sum + int.from_bytes(x, "little")
            sum = sum + x
        sum ^= 0xffff
        sum += 1

        return sum
        
    def sendRequestInfo(self, requestData):
        
        data_to_send = [0xDD, 0xA5]
        if self.bmsState == Request.BASIC_INFO:
            dat = [0x03, 0x00]
            #print("Send Basic Request to BMS:", end=" ")
        elif self.bmsState == Request.CELL_VOLTAGE:
            dat = [0x04, 0x00]

        for x in dat:
            data_to_send.append(x)
            
        checksum = self.calcChecksum(dat)
        data_to_send.append(checksum>>8)
        data_to_send.append(checksum&0x00FF)
        data_to_send.append(0x77)
        
        #for y in data_to_send:
        #    print(hex(y), end=" ")
        #print()
        
        self.serialBMS.write(data_to_send)    

    def evalData(self, data):
        #print(data)
        if self.bmsState == Request.BASIC_INFO:
            self.total_voltage = data[2]<<8 | data[3]
            
            if data[4] >=127:   #bit3 gesetzt = negatives vorzeichen
                self.current = data[4]<<8 | data[5]
                self.current = (65536-self.current)*-1  #bit15 abziehen = vorzeichen 65536 = 1xxxx xxxx xxxx xxxx
            else:
                self.current = data[4]<<8 | data[5]
            
            self.residual_capacity_ = data[6]<<8 | data[7]
            self.nominal_capacity_ = data[8]<<8 | data[9]
            self.cycle_life_ = data[10]<<8 | data[11]
            self.product_data_ = data[12]<<8 | data[13]
            self.balance_status_low_ = data[14]<<8 | data[15]
            self.balance_status_high_ = data[16]<<8 | data[17]
            self.protection_status_ = data[18]<<8 | data[19]
            self.version_info_ = data[20]
            self.rsoc = data[21]
            self.fet_controll_status = data[22]
            self.cell_block_serie = data[23]
            self.NTC_sensor_numbers = data[24]
            self.sensor_values.clear()
            
            for i in range(self.NTC_sensor_numbers):
                temp= (data[25+i*2]<<8 | data[26+i*2]) - 2731   # 273,1C abziehen 
                temp=temp/10
                self.sensor_values.append(temp)
                #print("Temperatur: ", temp)
            self.last_updateBasicInfo = current_milli_time()

        elif self.bmsState == Request.CELL_VOLTAGE:
            self.cellVoltages.clear()
            numCellvoltages = int((data[0]<<8 | data[1])/2)
            for i in range(numCellvoltages):
                self.cellVoltages.append(data[2+i*2]<<8 | data[3+i*2])
            self.last_updateCellVoltages = current_milli_time()

        self.bmsState =Request.NONE


    def printData(self):
        print("Print BMS Data:")
        
        print("_________________________________________________")
        print("Voltage:              {} V".format(self.total_voltage/100))
        print("Current:                  {} A".format(self.current))
        print("Capacity:              {} Ah".format(self.residual_capacity_/100))
        print("Capacity:              {} Ah".format(self.nominal_capacity_/100))
        print("Cycle Life:               {}".format(self.cycle_life_))
        print("Product Data:        0x{:04x}".format(self.product_data_))
        print("Balance Low:         0x{:04x}".format(self.balance_status_low_))#ersten 16 Zellen
        print("Balance High:        0x{:04x}".format(self.balance_status_high_))#weiteren 16 Zellen
        print("Prot Status:         0x{:04x}".format(self.protection_status_))
        #protection status Beschreibung:    * bit0 Cell Block Over Vol * bit1 Cell Block Under Vol * bit2 Battery Over Vol * bit3 Battery Under Vol * bit4 Charging Over temp * bit5 Charging Low temp * bit6 Discharging Over temp * bit7 Discharging Low temp * bit8 Charging Over current * bit9 Discharging Over current * bit10 Short Circuit * bit11 Fore end IC Error * bit12 MOS Software Lock in * bit13~bit15 Reserve
        print("Version:               0x{:02x}".format(self.version_info_))
        print("RSOC:                    {} %".format(self.rsoc))
        print("FET:                   0x{:02x}".format(self.fet_controll_status))
        print("Num Cells:                {}".format(self.cell_block_serie))
        print("Num NTC sensor:           {}".format(self.NTC_sensor_numbers))
        for i in range(self.NTC_sensor_numbers):
            print("Temp {}:                {}".format(i,self.sensor_values[i]))
        #print("Temp 2:                {}".format(self.sensor_values[1]))
        print("Last Basic info Update:      {}".format(self.last_updateBasicInfo))
        for i in range(len(self.cellVoltages)):
            print("Cell Voltage {}:                {}".format(i,self.cellVoltages[i]))
        print("Last cell voltage Update:      {}".format(self.last_updateCellVoltages))
        print("_________________________________________________")
        
        
    def sendDataToMain(self):
        bms_output ={}

        #Gesamt Spannung
        spannung = self.total_voltage/100
        bms_output.update({'Spannung': spannung})

        ######Strom
        strom = self.current/100
        bms_output.update({'Strom': strom})
       
        #SoC
        SoC = self.rsoc
        bms_output.update({'SoC': SoC})
        
        #Temperatur
        temp1 = -273.15
        temp2 = -273.15
        temp3 = -273.15
        temp4 = -273.15
        temp5 = -273.15
        temp6 = -273.15
        temp7 = -273.15
        temp8 = -273.15
        '''
        for i in range(self.NTC_sensor_numbers):
            temp_name = 'temp'+str(i+1)
            vars()[temp_name] = self.sensor_values[i]
        '''
        for i in range(self.NTC_sensor_numbers):
            if i ==0:
                temp1 = self.sensor_values[i]
            elif i ==1:
                temp2 = self.sensor_values[i]
            elif i ==2:
                temp3 = self.sensor_values[i]
        bms_output.update({'Temperatur 1': temp1, 'Temperatur 2': temp2, 'Temperatur 3': temp3, 'Temperatur 4': temp4, 'Temperatur 5': temp5, 'Temperatur 6': temp6, 'Temperatur 7': temp7, 'Temperatur 8': temp8})
       
       
        #maximale Zellspannung
        max_Zellspg = max(self.cellVoltages, default=5000)
        max_Zellspg = max_Zellspg/1000
        if max_Zellspg == 5:
            position_max_Zellspg = 0
        else:
            position_max_Zellspg = self.cellVoltages.index(max(self.cellVoltages)) + 1
        bms_output.update({'maximale Zellspannung': max_Zellspg, 'Position maximale Zellspannung': position_max_Zellspg})
                
        #minimale Zellspannung
        min_Zellspg = min(self.cellVoltages, default = 0)
        min_Zellspg = min_Zellspg/1000
        if min_Zellspg == 0:
            position_min_Zellspg = 0
        else:
            position_min_Zellspg = self.cellVoltages.index(min(self.cellVoltages)) + 1
        bms_output.update({'minimale Zellspannung': min_Zellspg, 'Position minimale Zellspannung': position_min_Zellspg})
    
        #Isolationswiderstand [kOhm] Gehäuse gegen PLUS  
        isoR_G_plus = 38

        #Isolationswiderstand [kOhm] Gehäuse gegen MINUS  
        isoR_G_minus = 38

        #spezifischer Isolationswiderstand [Ohm/V] Gehäuse gegen PLUS  
        spez_isoR_G_plus = 50

        #spezifischer Isolationswiderstand [Ohm/V] Gehäuse gegen MINUS  
        spez_isoR_G_minus = 50
        bms_output.update({'Isolationswiderstand Gehäuse gegen PLUS': isoR_G_plus, 'Isolationswiderstand Gehäuse gegen MINUS': isoR_G_minus, 'spezifischer Isolationswiderstand Gehäuse gegen PLUS': spez_isoR_G_plus, 'spezifischer Isolationswiderstand Gehäuse gegen MINUS': spez_isoR_G_minus})        
        
        bms_output.update({'Protection Status': self.protection_status_, 'Balance Status': self.balance_status_low_})
        
        
        ### fix values
        #Anzahl der Seriell-Verbindungen [1]
        n_Zellen = self.cell_block_serie
        bms_output.update({'Anzahl der Seriell-Verbindungen': n_Zellen})
        
        #maximal erlaubte Zellspannung [V]
        max_zellspg_erlaubt = 4.25
        bms_output.update({'maximal erlaubte Zellspannung': max_zellspg_erlaubt})
        
        #minimal erlaubte Zellspannung [V]
        min_zellspg_erlaubt = 2.7
        bms_output.update({'minimal erlaubte Zellspannung': min_zellspg_erlaubt})
        
        #maximal erlaubte Batteriespannung [V]
        max_battspg_erlaubt = 55.25
        bms_output.update({'maximal erlaubte Batteriespannung': max_battspg_erlaubt})
        
        #minimal erlaubte Batteriespannung [V]
        min_battspg_erlaubt = 35.1
        bms_output.update({'minimal erlaubte Batteriespannung': min_battspg_erlaubt})
        
        #maximaler Entladestrom [A]
        max_Entl = 60
        bms_output.update({'maximaler Entladestrom': max_Entl})
        
        #maximaler Ladestrom [A]
        max_Lade = 60
        bms_output.update({'maximaler Ladestrom': max_Lade})
        
        #Minimale Temperatur Laden  [°C]
        min_Temp_laden = 5
        bms_output.update({'Minimale Temperatur Laden': min_Temp_laden})
        
        #Maximale Temperatur Laden  [°C]
        max_Temp_laden = 60
        bms_output.update({'Maximale Temperatur Laden': max_Temp_laden})
        
        #Minimale Temperatur Entladen [°C]
        min_Temp_entl = 0
        bms_output.update({'Minimale Temperatur Entladen': min_Temp_entl})
        
        #Maximale Temperatur Laden [°C]
        max_Temp_entl = 65
        bms_output.update({'Maximale Temperatur Entladen': max_Temp_entl})
        
        #Fehlerauslösezeit [s]
        Fehlerzeit = 5
        bms_output.update({'Fehlerauslösezeit': Fehlerzeit})
        
        #nominelle Spannung [V]
        nom_Spannung = 48.1
        bms_output.update({'nominelle Spannung': nom_Spannung})
        
        #nominelle Kapazität [Ah]
        nom_Kapazität = 52.0
        bms_output.update({'nominelle Kapazität': nom_Kapazität})
        
        #nominelle Energie [Wh]
        nom_Energie = int(nom_Spannung * nom_Kapazität)
        bms_output.update({'nominelle Energie': nom_Energie})
        
        #Ladeschlussspannung [V]
        lad_Spannung = n_Zellen * 4.2
        bms_output.update({'Ladeschlussspannung': lad_Spannung})
        
        #Ladestrom [A]
        if n_Zellen == 7:
            lad_Strom =  100
        elif n_Zellen == 13:
            lad_Strom =  50
        else: 
            lad_Strom = 0
        bms_output.update({'Ladestrom': lad_Strom})
        
        
        #print(bms_output)
        self.outBmsQueue.put(bms_output) 
        
        #print("send BMS Data ")
        #print("_________________________________________________")

        
        
        
    # Thread
    def run(self):
        if self.debugOutput:
            print("smartBMS: Run - Start Thread")
        incData = []
        shortData = []
        incomingDataTime = int(round(time.time() * 1000))
        self.running = True
    
        while(self.running):
            time.sleep(.01)   #wichtig sonst 100% cpu auslastung
            try:
                ret = self.serialBMS.read(200)      #read 200byte, serial timeout 0.2sec
                #if ret:
                #    print("Serial Return:", ret)
                    
                #incData = []
                if ret:
                    # something arrived, save data as ints in list of ints
                    for element in ret:
                        incData.append(element)
                        #print(element)
                    incomingDataTime = int(round(time.time() * 1000))
                    #print("smartBMS: incData = {}".format(incData) )
                    
                #check if timeout occured and process data if so
                if (int(round(time.time() * 1000)) - incomingDataTime)>250 and incData :
                    #print("smartBMS: incData = {}".format(incData) )
                    
                    if incData[0] == 0xDD:
                        
                        shortData = incData[2:(len(incData)-3)]
                        #print(shortData)
                        checksum = self.calcIncChecksum(shortData)
                        #if checksum == (int.from_bytes(incData[len(incData)-3], "little")*256 + int.from_bytes(incData[len(incData)-2], "little")):
                        #print(checksum, (incData[len(incData)-3]*256 + incData[len(incData)-2]))
                        if checksum == (incData[len(incData)-3]*256 + incData[len(incData)-2]):
                            # checksum is correct, do further processing
                            self.evalData(shortData)
                            #self.printData()
                        else:
                            print("checksum error")
                            incData = []
                    #reset buffer
                    incData = []
            except:
                pass
            
            
            #check for incoming data from main thread
            try:
                qDataIn = self.inBmsQueue.get_nowait()
                if(qDataIn=="SIG-INT"):
                    # end thread
                    if self.debugOutput:
                        print("smartBMS: End - SIG-INT arrived")
                    self.running = False
                    self.serialBMS.close()

                #if(qDataIn=="PRINT"):
                    #self.printData()

            except:
                # do nothing
                pass
            
            
            if (current_milli_time() - self.last_updateBasicInfo)>self.updateCycle and self.bmsState == Request.NONE:
                #last_updateBasicInfo wird in function evalData gesetzt, zeit seit letztem daten auslsesn
                #updatecycle wird an Class übergeben (1 sec interval)
                self.bmsState = Request.BASIC_INFO              #Frage basic Information vom BMS ab (Spannung, Strom, Soc, Temperatur)
                self.lastrequest = current_milli_time()         #wird für timeput abfrage unten gesetzt
                if self.debugOutput:
                        print("smartBMS: Run - Basic Info ")
                self.sendRequestInfo(Request.BASIC_INFO)        #hex srting für Basic INfo an BMS senden
                self.sendDataToMain()                           #BMS Daten aufbereiten und in queue stellen

            elif (current_milli_time() - self.last_updateCellVoltages)>self.updateCycle and self.bmsState == Request.NONE:
                self.bmsState = Request.CELL_VOLTAGE
                self.lastrequest = current_milli_time()        #wird für timeput abfrage unten gesetzt
                if self.debugOutput:
                        print("smartBMS: Run - Cell Voltage ")
                self.sendRequestInfo(Request.CELL_VOLTAGE)
            
            
            if (current_milli_time() - self.lastrequest)>self.requestTimout and self.bmsState != Request.NONE:
                print("smartBMS: Request Timeout ")
                self.bmsState = Request.NONE   

            # check if data need to be updated in the main
            if(current_milli_time() - self.lastNotifyTime > self.updateCycle):
                self.lastNotifyTime = current_milli_time()
                self.sendDataToMain()

            
            
        if self.debugOutput:
            print("smartBMS: Thread exit")
