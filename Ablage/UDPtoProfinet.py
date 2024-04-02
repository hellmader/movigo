#!/usr/bin/python

########################################################################
# V1.0
########################################################################

import serial
import time
import threading
from multiprocessing import Queue
import enum
import numpy as np
import can

class Request(enum.Enum):
    NONE = 0
    BASIC_INFO = 1
    CELL_VOLTAGE = 2


class UDPtoProfinet(threading.Thread):
    def __init__(self, debugOutput, updateCycle, inUDPtoProfinet):
        threading.Thread.__init__(self)
        self.debugOutput = debugOutput
        self.updateCycle = updateCycle
        self.inUDPtoProfinet = inUDPtoProfinet
        if self.debugOutput:
            print("UDPtoProfinet: Init - Debug enabled")
        # open serial port
        if self.debugOutput:
            print("UDPtoProfinet: Init - Open Serial Port")
        self.can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan', bitrate=250000)# socketcan_native
        
        self.data_spannung = 0
        self.data_strom = 0
        self.data_SoC = 0
        self.data_Temp1 = 0
        self.data_Temp2 = 0
        self.data_max_Entl = 0
        self.data_max_Lade = 0
        self.data_max_Zellspg = 0
        self.data_min_Zellspg = 0
        self.data_n_Zellen = 0
        self.data_min_Temp_laden = 0
        self.data_max_Temp_laden = 0
        self.data_min_Temp_entl = 0
        self.data_max_Temp_entl = 0
        self.data_isoR_G_plus = 0
        self.data_isoR_G_minus = 0
        self.data_spez_isoR_G_plus = 0
        self.data_spez_isoR_G_minus = 0
        self.Status_Bits = 0
        self.Warning_Bits = 0
        self.Error_Bits = 0
        
        
        
        
        
        
        self.CAN_ID_spannung = 0x201
        self.CAN_ID_strom = 0x202
        self.CAN_ID_SoC = 0x203
        self.CAN_ID_temp1 = 0x204
        self.CAN_ID_temp2 = 0x205
        self.CAN_ID_max_Entl = 0x206
        self.CAN_ID_max_Lade = 0x207
        self.CAN_ID_max_Zellspg = 0x208
        self.CAN_ID_min_Zellspg = 0x209
        self.CAN_ID_n_Zellen = 0x210
        self.CAN_ID_min_Temp_laden = 0x211
        self.CAN_ID_max_Temp_laden = 0x212
        self.CAN_ID_min_Temp_entl = 0x213
        self.CAN_ID_max_Temp_entl = 0x214
        self.CAN_ID_isoR_G_plu = 0x215
        self.CAN_ID_isoR_G_minus = 0x216
        self.CAN_ID_spez_isoR_G_plus = 0x217
        self.CAN_ID_spez_isoR_G_minus = 0x218
        self.CAN_ID_status = 0x230
        self.CAN_ID_warning = 0x231
        self.CAN_ID_error = 0x232
        
    def sendCANtoProfinet(self,data):
        #print('CAN',data)
        #{'Spannung': 5252, 'Strom': -289, 'SoC': 13, 'Temperatur 1': 2943, 'Temperatur 2      ': 2943, 'maximaler Entladestrom': 60, 'maximaler Ladestrom': 60, 'maximale Zell      spannung': 3774, 'Position maximale Zellspannung': 8, 'minimale Zellspannung': 3      692, 'Position minimale Zellspannung': 13, 'Anzahl der Seriell-Verbindungen': 14      , 'Minimale Temperatur Laden': 10, 'Maximale Temperatur Laden': 40, 'Minimale Te      mperatur Entladen': 0, 'Maximale Temperatur Entladen ': 65, 'Isolationswiderstan      d kOhm Gehäuse gegen PLUS': 38, 'Isolationswiderstand kOhm Gehäuse gegen MINUS':       38, 'spezifischer Isolationswiderstand Ohm/V Gehäuse gegen PLUS': 50, 'spezifis      cher Isolationswiderstand Ohm/V Gehäuse gegen MINUS': 50, 'Status': 261, 'Warnin      g': 32, 'Error': 0}

        
        #Gesamt Spannung
        spannung = data['Spannung']
        self.data_spannung = int(spannung).to_bytes(2, 'big')
        msg = can.Message(arbitration_id=self.CAN_ID_spannung, data=self.data_spannung, extended_id=False)
        self.can0.send(msg)
        
        ######Strom
        strom = data['Strom']
        if strom <0:
            vorzeichen=255
            self.data_strom = int(vorzeichen).to_bytes(1, 'big') + int(abs(strom)).to_bytes(2, 'big')
        else:
            vorzeichen=0
            self.data_strom = int(vorzeichen).to_bytes(1, 'big') + int(strom).to_bytes(2, 'big')
        
        msg = can.Message(arbitration_id=self.CAN_ID_strom, data=self.data_strom, extended_id=False)
        self.can0.send(msg)
        
        #SoC
        SoC = data['SoC']
        self.data_SoC = int(SoC).to_bytes(1, 'big')
        msg = can.Message(arbitration_id=self.CAN_ID_SoC, data=self.data_SoC, extended_id=False)
        self.can0.send(msg)
        
        #Temperatur 1
        Temp1 = data['Temperatur 1']
        self.data_Temp1 = int(Temp1/100).to_bytes(1, 'big')
        msg = can.Message(arbitration_id=self.CAN_ID_temp1, data=self.data_Temp1, extended_id=False)
        self.can0.send(msg)
                
        #Temperatur 2
        Temp2 = data['Temperatur 2']
        self.data_Temp2 = int(Temp2/100).to_bytes(1, 'big')
        msg = can.Message(arbitration_id=self.CAN_ID_temp2, data=self.data_Temp2, extended_id=False)
        self.can0.send(msg)      
        
        #maximaler Entladestrom
        max_Entl = data['maximaler Entladestrom']
        self.data_max_Entl = int(max_Entl).to_bytes(1, 'big')
        msg = can.Message(arbitration_id=self.CAN_ID_max_Entl, data=self.data_max_Entl, extended_id=False)
        self.can0.send(msg)      
        
        #maximaler Ladestrom
        max_Lade = data['maximaler Ladestrom']
        self.data_max_Lade = int(max_Lade).to_bytes(1, 'big')
        msg = can.Message(arbitration_id=self.CAN_ID_max_Lade, data=self.data_max_Lade, extended_id=False)
        self.can0.send(msg)            
        
        #maximale Zellspannung
        max_Zellspg = data['maximale Zellspannung']
        position_max_Zellspg = data['Position maximale Zellspannung']
        self.data_max_Zellspg = int(position_max_Zellspg).to_bytes(1, 'big') +  int(max_Zellspg).to_bytes(2, 'big')
        msg = can.Message(arbitration_id=self.CAN_ID_max_Zellspg, data=self.data_max_Zellspg, extended_id=False)
        self.can0.send(msg)
                
        #minimale Zellspannung
        min_Zellspg = data['minimale Zellspannung']
        position_min_Zellspg = data['Position minimale Zellspannung']
        self.data_min_Zellspg = int(position_min_Zellspg).to_bytes(1, 'big') + int(min_Zellspg).to_bytes(2, 'big')
        msg = can.Message(arbitration_id=self.CAN_ID_min_Zellspg, data=self.data_min_Zellspg, extended_id=False)
        self.can0.send(msg)        
        
        #Anzahl der Seriell-Verbindungen
        n_Zellen = data['Anzahl der Seriell-Verbindungen']
        self.data_n_Zellen = int(n_Zellen).to_bytes(1, 'big')
        msg = can.Message(arbitration_id=self.CAN_ID_n_Zellen, data=self.data_n_Zellen, extended_id=False)
        self.can0.send(msg)
        
        #Minimale Temperatur Laden 
        min_Temp_laden = data['Minimale Temperatur Laden']
        self.data_min_Temp_laden = int(min_Temp_laden).to_bytes(1, 'big')
        msg = can.Message(arbitration_id=self.CAN_ID_min_Temp_laden, data=self.data_min_Temp_laden, extended_id=False)
        self.can0.send(msg) 
                
        #Maximale Temperatur Laden 
        max_Temp_laden = data['Maximale Temperatur Laden']
        self.data_max_Temp_laden = int(max_Temp_laden).to_bytes(1, 'big')
        msg = can.Message(arbitration_id=self.CAN_ID_max_Temp_laden, data=self.data_max_Temp_laden, extended_id=False)
        self.can0.send(msg)        
           
        #Minimale Temperatur Entladen 
        min_Temp_entl = data['Minimale Temperatur Entladen']
        self.data_min_Temp_entl = int(min_Temp_entl).to_bytes(1, 'big')
        msg = can.Message(arbitration_id=self.CAN_ID_min_Temp_entl, data=self.data_min_Temp_entl, extended_id=False)
        self.can0.send(msg) 
                
        #Maximale Temperatur Laden 
        max_Temp_entl = data['Maximale Temperatur Entladen']
        self.data_max_Temp_entl = int(max_Temp_entl).to_bytes(1, 'big')
        msg = can.Message(arbitration_id=self.CAN_ID_max_Temp_entl, data=self.data_max_Temp_entl, extended_id=False)
        self.can0.send(msg) 
    
        #Isolationswiderstand [kOhm] Gehäuse gegen PLUS  
        isoR_G_plus = data['Isolationswiderstand kOhm Gehäuse gegen PLUS']
        self.data_isoR_G_plus = int(isoR_G_plus).to_bytes(1, 'big')
        msg = can.Message(arbitration_id=self.CAN_ID_isoR_G_plu, data=self.data_isoR_G_plus, extended_id=False)
        self.can0.send(msg)
        
        #Isolationswiderstand [kOhm] Gehäuse gegen MINUS  
        isoR_G_minus = data['Isolationswiderstand kOhm Gehäuse gegen MINUS']
        self.data_isoR_G_minus = int(isoR_G_minus).to_bytes(1, 'big')
        msg = can.Message(arbitration_id=self.CAN_ID_isoR_G_minus, data=self.data_isoR_G_minus, extended_id=False)
        self.can0.send(msg)
    
        #spezifischer Isolationswiderstand [Ohm/V] Gehäuse gegen PLUS  
        spez_isoR_G_plus = data['spezifischer Isolationswiderstand Ohm/V Gehäuse gegen PLUS']
        self.data_spez_isoR_G_plus = int(spez_isoR_G_plus).to_bytes(1, 'big')
        msg = can.Message(arbitration_id=self.CAN_ID_spez_isoR_G_plus, data=self.data_spez_isoR_G_plus, extended_id=False)
        self.can0.send(msg)
    
        #spezifischer Isolationswiderstand [Ohm/V] Gehäuse gegen MINUS  
        spez_isoR_G_minus = data['spezifischer Isolationswiderstand Ohm/V Gehäuse gegen MINUS']
        self.data_spez_isoR_G_minus = int(spez_isoR_G_minus).to_bytes(1, 'big')
        msg = can.Message(arbitration_id=self.CAN_ID_spez_isoR_G_minus, data=self.data_spez_isoR_G_minus, extended_id=False)
        self.can0.send(msg)    
        
        #Status Bits
        self.Status_Bits = data['Status']
        data_Status_Bits = int(self.Status_Bits).to_bytes(2, 'big')
        msg = can.Message(arbitration_id=self.CAN_ID_status, data=data_Status_Bits, extended_id=False)
        self.can0.send(msg) 
        
        #Warning Bits
        self.Warning_Bits = data['Warning']
        data_Warning_Bits = int(self.Warning_Bits).to_bytes(1, 'big')
        msg = can.Message(arbitration_id=self.CAN_ID_warning, data=data_Warning_Bits, extended_id=False)
        self.can0.send(msg) 
        
        #Error Bits
        self.Error_Bits = data['Error']
        data_Error_Bits = int(self.Error_Bits).to_bytes(1, 'big')
        msg = can.Message(arbitration_id=self.CAN_ID_error, data=data_Error_Bits, extended_id=False)
        self.can0.send(msg)
 
        
        
    def printsendCANtoProfinet(self):
        print("send CAN Data")
        print("_________________________________________________")
        
        print('Spannung in HEX: '+str(self.data_spannung.hex()) + ' an CAN-ID ' + str(hex(self.CAN_ID_spannung)))
        print('Strom in HEX: '+str(self.data_strom.hex()) + ' an CAN-ID ' + str(hex(self.CAN_ID_strom)))
        print('SoC in HEX: '+str(self.data_SoC.hex()) + ' an CAN-ID ' + str(hex(self.CAN_ID_SoC)))
        print('Temperatur 1 in HEX: '+str(self.data_Temp1.hex()) + ' an CAN-ID ' + str(hex(self.CAN_ID_temp1)))
        print('Temperatur 2 in HEX: '+str(self.data_Temp2.hex()) + ' an CAN-ID ' + str(hex(self.CAN_ID_temp2))) 
        print('maximaler Entladestrom in HEX: '+str(self.data_max_Entl.hex()) + ' an CAN-ID ' + str(hex(self.CAN_ID_max_Entl))) 
        print('maximaler Ladestrom in HEX: '+str(self.data_max_Lade.hex()) + ' an CAN-ID ' + str(hex(self.CAN_ID_max_Lade))) 
        print('maximale Zellspannung in HEX: '+str(self.data_max_Zellspg.hex()) + ' an CAN-ID ' + str(hex(self.CAN_ID_max_Zellspg))) 
        print('minimale Zellspannung in HEX: '+str(self.data_min_Zellspg.hex()) + ' an CAN-ID ' + str(hex(self.CAN_ID_min_Zellspg)))  
        print('Anzahl der Seriell-Verbindungen in HEX: '+str(self.data_n_Zellen.hex()) + ' an CAN-ID ' + str(hex(self.CAN_ID_n_Zellen)))  
        print('minimale Ladetemperatur in HEX: '+str(self.data_min_Temp_laden.hex()) + ' an CAN-ID ' + str(hex(self.CAN_ID_min_Temp_laden))) 
        print('maximale Ladetemperatur in HEX: '+str(self.data_max_Temp_laden.hex()) + ' an CAN-ID ' + str(hex(self.CAN_ID_max_Temp_laden)))  
        print('minimale Entladetemperatur in HEX: '+str(self.data_min_Temp_entl.hex()) + ' an CAN-ID ' + str(hex(self.CAN_ID_min_Temp_entl))) 
        print('maximale Entladetemperatur in HEX: '+str(self.data_max_Temp_entl.hex()) + ' an CAN-ID ' + str(hex(self.CAN_ID_max_Temp_entl))) 
        print('Isolationswiderstand Gehäuse gegen PLUS  in HEX: '+str(self.data_isoR_G_plus.hex()) + ' an CAN-ID ' + str(hex(self.CAN_ID_isoR_G_plu)))  
        print('Isolationswiderstand Gehäuse gegen MINUS  in HEX: '+str(self.data_isoR_G_minus.hex()) + ' an CAN-ID ' + str(hex(self.CAN_ID_isoR_G_minus)))
        print('spezifischer Isolationswiderstand Gehäuse gegen PLUS  in HEX: '+str(self.data_spez_isoR_G_plus.hex()) + ' an CAN-ID ' + str(hex(self.CAN_ID_spez_isoR_G_plus)))  
        print('spezifischer Isolationswiderstand Gehäuse gegen MINUS  in HEX: '+str(self.data_spez_isoR_G_minus.hex()) + ' an CAN-ID ' + str(hex(self.CAN_ID_spez_isoR_G_minus)))  
        print('Status Bits: '+str(bin(self.Status_Bits)) + ' an CAN-ID ' + str(hex(self.CAN_ID_status)))
        print('Warning Bits: '+str(bin(self.Warning_Bits)) + ' an CAN-ID ' + str(hex(self.CAN_ID_warning))) 
        print('Error Bits: '+str(bin(self.Error_Bits)) + ' an CAN-ID ' + str(hex(self.CAN_ID_error)))
        
    def run(self):
        if self.debugOutput:
            print("can: Run - Start Thread")
        incData = []
        self.running = True
        incomingDataTime = int(round(time.time() * 1000))
    
        while(self.running):
            #check for incoming data from main thread
            try:
                #if(self.sendInProgress==False):
                qDataIn = self.inUDPtoProfinet.get()
                print('111111111111111111111111111111111111111111111111111111111', qDataIn)
                if(qDataIn=="SIG-INT"):
                    # end thread
                    if self.debugOutput:
                        print("Can: End - SIG-INT arrived")
                    self.running = False
                    
                elif(qDataIn!=None):
                    self.sendCANtoProfinet(qDataIn)
                    self.printsendCANtoProfinet()
                    
            except:
                # do nothing
                pass

        if self.debugOutput:
                print("canO: Thread exit")
