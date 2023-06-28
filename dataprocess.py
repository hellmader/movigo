#!/usr/bin/python

########################################################################
# V1.0
########################################################################


import time
import enum
import os
import logging

class Request(enum.Enum):
    NONE = 0
    BASIC_INFO = 1
    CELL_VOLTAGE = 2


def current_milli_time():
    return round(time.time() * 1000)

class dataprocessing():
    def __init__(self):#, to_smartBMS, from_CtPN, to_CtPN, from_charger, to_charger, from_IOs, to_IOs):
        
        #self.from_smartBMS = from_smartBMS
        '''
        self.to_smartBMS = to_smartBMS
        self.from_CtPN = from_CtPN
        self.to_CtPN = to_CtPN
        self.from_charger = from_charger
        self.to_charger = to_charger
        self.from_IOs = from_IOs
        self.to_IOs = to_IOs
        '''
        # hier die Daten die lokal gespeichert werden sollen erstmal deklarieren
        # BMS Variables
        self.voltage = 0
        self.current = 0
        self.SoC = 0
        self.mintemp = 0
        self.maxtemp = 0
        self.max_discharge_current = 0
        self.max_charge_current = 0
        self.max_cell_voltage = 0
        self.pos_max_voltage = 0
        self.min_cell_voltage = 0
        self.pos_min_voltage = 0
        self.num_of_cells = 0
        self.min_temp_charge = 0
        self.max_temp_charge = 0
        self.min_temp_discharge = 0
        self.max_temp_discharge = 0
        self.isolation_case_plus = 0
        self.isolation_case_minus = 0
        self.spez_isolation_case_plus = 0
        self.spez_isolation_case_minus = 0
        self.protection_status = 0
        self.balance_status_low = 0
        self.parameterBMS = 0
        
        #Ladegeräte Variables
        self.Spannung_Ladegeraet = 0
        self.Strom_Ladegeraet = 0
        self.Status_Ladegeraet = 64
        self.Kommunikation_Ladegeraet = False
        self.Flag_geladen = False
        
        # Status Variables
        self.Status_A0_AUX1 = 1
        self.Status_A1_AUX2 = 1
        self.Status_A2_AUX3 = 0
        self.Status_A3_AUX4 = 0
        self.Status_A4_P_plus = 0
        self.Status_A5_C_plus = 0
        self.Status_A6_Balancing = 0
        self.Status_A7_Ladegerät_present = 0
        self.Status_B0_Ladegerät_aktiv = 0
        self.Status_B1_Ladevorgang_beendet = 0
        self.Status_B2_bereit = 0
        self.Status_B3_reserved1 = 0
        self.Status_B4_reserved2 = 0
        self.Status_B5_reserved3 = 0
        self.Status_B6_reserved4 = 0
        self.Status_B7_reserved5 = 0
        
        self.Status_Relais = 1
        
        #Warning Variables
        self.Warning_A0_Zell_max = 1
        self.Warning_A1_Zell_min = 1
        self.Warning_A2_Temp_max_entl = 1
        self.Warning_A3_Temp_min_entl = 1
        self.Warning_A4_Temp_max_laden = 1
        self.Warning_A5_Temp_min_laden = 1
        self.Warning_A6_Strom_entl = 1
        self.Warning_A7_Strom_laden = 1        
        self.Warning_B0_isolation = 1
        self.Warning_B1_Akku_disbalance = 1
        self.Warning_B2_SoC_min = 1
        self.Warning_B3_reserved1 = 0
        self.Warning_B4_reserved2 = 0
        self.Warning_B5_reserved3 = 0
        self.Warning_B6_reserved4 = 0
        self.Warning_B7_reserved5 = 0  
        
        #Error Variables
        self.Error_A = 1
        self.Error_B = 0
        self.Error_A0_Zell_min = 1
        self.Error_A1_Zell_max = 1
        self.Error_A2_Temp_max_entl = 1
        self.Error_A3_Temp_min_entl = 1
        self.Error_A4_Temp_max_laden = 1
        self.Error_A5_Temp_min_laden = 1
        self.Error_A6_Strom_entl = 1
        self.Error_A7_Strom_laden = 1
        self.Error_B0_isolation = 1
        self.Error_B1_Comm_Timeout = 1
        self.Error_B2_Fehler = 1
        self.Error_B3_reserved1 = 0
        self.Error_B4_reserved2 = 0
        self.Error_B5_reserved3 = 0
        self.Error_B6_reserved4 = 0
        self.Error_B7_reserved5 = 0  
        
        self.Chargerate = 1
        self.FA1 = 0
        self.FA2 = 0
        self.Request_AUX2 = 0
        self.Request_AUX3 = 0
        self.Request_AUX4 = 0
        self.Request_P = 0
        self.Request_C = 0
        self.Request_sleep = 0
        self.Requests = {'Status_AUX1':1, 'Request_AUX2':1, 'Request_AUX3':0, 'Request_AUX4':0, 'Request_P':0, 'Request_C':0, 'Request_sleep':0}
        #self.Requests = {'Status_AUX1':self.Status_A0_AUX1, 'Request_AUX2':self.Request_AUX2,'Request_P':self.Request_P, 'Request_C':self.Request_C, 'Request_sleep':self.Request_sleep}
        
        #Thingsboard
        self.Akkuname = ""
        
        #shutdown
        self.shutdown = False
        self.Update_time_sleep =0 
        
        
   
    
    def updateBMS(self, qDatafromBMS):
        #print (qDatafromBMS)
        self.parameterBMS = qDatafromBMS
        self.current = qDatafromBMS['Strom']
        self.SoC = qDatafromBMS['SoC']
        self.maxtemp = max(qDatafromBMS['Temperatur 1'], qDatafromBMS['Temperatur 2'], qDatafromBMS['Temperatur 3'], qDatafromBMS['Temperatur 4'])
        
        if qDatafromBMS['Temperatur 3'] <-200:
            self.mintemp = min(qDatafromBMS['Temperatur 1'], qDatafromBMS['Temperatur 2'])
        elif qDatafromBMS['Temperatur 4'] <-200:
            self.mintemp = min(qDatafromBMS['Temperatur 1'], qDatafromBMS['Temperatur 2'], qDatafromBMS['Temperatur 3'])
        else:
            self.mintemp = min(qDatafromBMS['Temperatur 1'], qDatafromBMS['Temperatur 2'], qDatafromBMS['Temperatur 3'], qDatafromBMS['Temperatur 4'])
        self.max_cell_voltage = qDatafromBMS['maximale Zellspannung']
        self.min_cell_voltage = qDatafromBMS['minimale Zellspannung']

        
        self.protection_status = qDatafromBMS['Protection Status']
        self.balance_status_low = qDatafromBMS['Balance Status']
        logging.info ('BMS Update abgeschlossen')

    def getBMSdata(self):
        return self.parameterBMS
        
        
    def DatafromProfinet(self, qData_fromProfinet):
        # qDataInfromProfinet hält die aktuellen daten von der Queue vom anderen Thread
        # -> die müssen hier gespeichert werden
        Chargerate = qData_fromProfinet['Chargerate']
        Controlbits = qData_fromProfinet['Controlbits']
        self.Chargerate = float(Chargerate)
        #NAMES_CONTROLBITS = {0: "AUX2",1: "AUX3",2: "AUX4",3: "DischargeRelay",4: "ChargeRelay",5: "Sleep",6: "FC1",7: "FC2",}
        #Bit0 AUX2
        
        # sps wird nicht beachtet bei AUX2
        self.Request_AUX2 = 1 #int(bin(Controlbits>>0)[-1])
        #if bin(Controlbits>>0)[-1]=='0':
        #    self.Request_AUX2 = 0
        #else:
        #    self.Request_AUX2 = 1
   
        #Bit1 AUX3
        self.Request_AUX3 = int(bin(Controlbits>>1)[-1])
        #if bin(Controlbits>>1)[-1]=='0':
        #    self.Request_AUX3 = 0
        #else:
        #    self.Request_AUX3 = 1   
        
        #Bit2 AUX4
        self.Request_AUX4 = int(bin(Controlbits>>2)[-1])
        #if bin(Controlbits>>2)[-1]=='0':
        #    self.Request_AUX4 = 0
        #else:
        #    self.Request_AUX4 = 1
        
        #Bit3 Freigabe P+
        self.Request_P = int(bin(Controlbits>>3)[-1])
        #if bin(Controlbits>>3)[-1]=='0':
        #    self.Request_P = 0
        #else:
        #    self.Request_P = 1
            
        #Bit4 Ladefreigabe
        self.Request_C = int(bin(Controlbits>>4)[-1])
        #if bin(Controlbits>>4)[-1]=='0':
        #    self.Request_C = 0
        #else:
        #    self.Request_C = 1
        
        #Bit5 Request Sleep
        if bin(Controlbits>>5)[-1]=='0':
            self.Request_sleep = 0
        else:
            self.Request_sleep = 1

            self.Status_A0_AUX1 = 1
            self.Request_AUX2 = 0
            self.Request_AUX3 = 0
            self.Request_AUX4 = 0
            self.Request_P = 0
            self.Request_C = 0
            self.Request_sleep = 1
            
            if self.shutdown == False:
                self.shutdown = True
                self.Update_time_sleep = time.time()*1000


        self.Requests = {'Status_AUX1':self.Status_A0_AUX1, 'Request_AUX2':self.Request_AUX2, 'Request_AUX3':self.Request_AUX3, 'Request_AUX4':self.Request_AUX4, 'Request_P':self.Request_P, 'Request_C':self.Request_C, 'Request_sleep':self.Request_sleep}


        logging.info('Requests {}'.format(self.Requests))
    
    def getChargeRate(self):
        return self.Chargerate
        
    def shutdown_code(self):
        if self.shutdown == True:
            os.system('sudo systemctl stop profinet')
            if (time.time()*1000 - self.Update_time_sleep > 10000):

                os.system('sudo shutdown -h now')

    def getRequests(self):
        return self.Requests
    
    def UpdateCANfromLadegeraet (self, data):
        
        if data == None:
            self.Status_A7_Ladegerät_present = 0
            self.Kommunikation_Ladegeraet = False
            self.Status_LadegeraetPresent=False
        else:
            self.Spannung_Ladegeraet = data['Ladegeraet Spannung']
            self.Strom_Ladegeraet = data['Ladegeraet Strom']
            self.Status_Ladegeraet = data['Ladegeraet Status']
            self.Status_LadegeraetPresent = data['Ladegeraet Present']
            self.Kommunikation_Ladegeraet = True
            
    def Ladegeraet_kommuniziert (self):
        return self.Kommunikation_Ladegeraet
                
    def Ladegeraet_present (self):
        if (self.Status_Ladegeraet <32) and (self.Status_LadegeraetPresent == True):
            self.Status_A7_Ladegerät_present = 1
        else:
            self.Status_A7_Ladegerät_present = 0
            self.Status_B0_Ladegerät_aktiv = 0
            self.Flag_geladen = False
            self.Status_B1_Ladevorgang_beendet = 0
            
    def Ladegeraet_aktiv (self):
        if (self.Status_Ladegeraet == 0) and (self.Strom_Ladegeraet>1):
            self.Status_B0_Ladegerät_aktiv = 1

                
    def Ladevorgang_beendet (self):
        if self.Strom_Ladegeraet>1:
            self.Flag_geladen = True
        if (self.Strom_Ladegeraet <5) and (self.Flag_geladen ==True):
            self.Status_B1_Ladevorgang_beendet = 1
            
    
    def Status_laden_beendet(self):
        return self.Status_B1_Ladevorgang_beendet == 1
            
    
    def Status_laden_bereit (self):
        if (self.Request_C == 1) and (self.Status_A7_Ladegerät_present == 1):
            return True
        else:
            self.Status_B0_Ladegerät_aktiv = 0
            self.Flag_geladen = False
            self.Status_B1_Ladevorgang_beendet = 0
            return False

    def Status_Relais_F(self,data):
        self.Status_Relais = data['Relais_error']

        if (self.Error_A and self.Error_B) == 0: #and (self.Status_Relais) == 0:
            self.Status_B2_bereit = 1
        else:
            self.Status_B2_bereit = 0
        

    def calculateStatusCodes(self, data):
        
        self.Status_A1_AUX2 = data['Status_AUX2']
        self.Status_A4_P_plus = data['Status_P']
        self.Status_A5_C_plus = data['Status_C']
        
        #Status Bits
        

        #Status_6_Balancing
        if self.balance_status_low==0:
            self.Status_A6_Balancing = 0
        else:
           self.Status_A6_Balancing = 1
   

        self.Status_A = self.Status_A7_Ladegerät_present*2**7 + self.Status_A6_Balancing*2**6 + self.Status_A5_C_plus*2**5 + self.Status_A4_P_plus*2**4 + self.Status_A3_AUX4*2**3 + self.Status_A2_AUX3*2**2 + self.Status_A1_AUX2*2**1 + self.Status_A0_AUX1
        
        self.Status_B = self.Status_B7_reserved5*2**7 + self.Status_B6_reserved4*2**6 + self.Status_B5_reserved3*2**5 + self.Status_B4_reserved2*2**4 + self.Status_B3_reserved1*2**3 + self.Status_B2_bereit*2**2 + self.Status_B1_Ladevorgang_beendet*2**1 + self.Status_B0_Ladegerät_aktiv
        
        
    def getStatusA(self):
        return self.Status_A
    def getStatusB(self):
        return self.Status_B
        
    def calculateWarningCodes(self):
        #Warning Bits

        #Warning_A0_Zell_max = 0
        if self.max_cell_voltage > 4.150:
            self.Warning_A0_Zell_max = 1
        else:
            self.Warning_A0_Zell_max = 0
            
        #Warning_A1_Zell_min
        if self.min_cell_voltage < 3.000:
            self.Warning_A1_Zell_min = 1
        else:
            self.Warning_A1_Zell_min = 0
            
        #Warning_A2_Temp_max_entl
        if (self.maxtemp > 60) and (self.current > 0):
            self.Warning_A2_Temp_max_entl = 1
        else:
            self.Warning_A2_Temp_max_entl = 0
        
        #Warning_A3_Temp_min_entl
        if (self.mintemp < 5) and (self.current > 0):
            self.Warning_A3_Temp_min_entl = 1
        else:
            self.Warning_A3_Temp_min_entl = 0
        
        #Warning_A4_Temp_max_laden
        if (self.maxtemp > 55) and (self.current < 0):
            self.Warning_A4_Temp_max_laden = 1
        else:
            self.Warning_A4_Temp_max_laden = 0
        
        #Warning_A5_Temp_min_laden
        if (self.mintemp < 10) and (self.current < 0):
            self.Warning_A5_Temp_min_laden = 1
        else:
            self.Warning_A5_Temp_min_laden = 0
        
        #Warning_A6_Strom_entl
        if self.current > 54.00:
            self.Warning_A6_Strom_entl = 1
        else:
            self.Warning_A6_Strom_entl = 0
            
        #Warning_A7_Strom_laden
        if self.current < -54.00:
            self.Warning_A7_Strom_laden = 1
        else:
            self.Warning_A7_Strom_laden = 0
        
        
        #Warning_B0_Isolationsfehler
        self.Warning_B0_isolation = 0
        
        #Warning_B1_Akku_disbalance
        if self.max_cell_voltage - self.min_cell_voltage > 0.100:
            self.Warning_B1_Akku_disbalance = 1
        else:
            self.Warning_B1_Akku_disbalance = 0
            
        #Warning_B2_SoC_min
        if self.SoC < 10:
            self.Warning_B2_SoC_min = 1
        else:
            self.Warning_B2_SoC_min = 0
        self.Warning_B3_reserved1 = 0
        self.Warning_B4_reserved2 = 0
        self.Warning_B5_reserved3 = 0
        self.Warning_B6_reserved4 = 0
        self.Warning_B7_reserved5 = 0  
      
        
        self.Warning_A = self.Warning_A7_Strom_laden*2**7 + self.Warning_A6_Strom_entl*2**6 + self.Warning_A5_Temp_min_laden*2**5 + self.Warning_A4_Temp_max_laden*2**4 + self.Warning_A3_Temp_min_entl*2**3 + self.Warning_A2_Temp_max_entl*2**2 + self.Warning_A1_Zell_min*2**1 + self.Warning_A0_Zell_max
        
        self.Warning_B = self.Warning_B7_reserved5*2**7 + self.Warning_B6_reserved4*2**6 + self.Warning_B5_reserved3*2**5 + self.Warning_B4_reserved2*2**4 + self.Warning_B3_reserved1*2**3 + self.Warning_B2_SoC_min*2**2 + self.Warning_B1_Akku_disbalance*2**1 + self.Warning_B0_isolation
        
    def getWarningA(self):
        return self.Warning_A
    def getWarningB(self):
        return self.Warning_B
 
        
    def calculateErrorCodes(self):
        # hier werden die berechnungen für error codes durchgeführt
        #Error Bits

        protection = int(self.protection_status)
        if protection // 2**15 == 1:
            #bit15 Reserve aktiv
            protection = protection % 2**15
            Fehler_15 = 1
        else:
            Fehler_15 = 0
            
        if protection // 2**14 == 1:
            #bit14 Reserve aktiv
            protection = protection % 2**14
            Fehler_14 = 1
        else:
            Fehler_14 = 0
            
        if protection // 2**13 == 1:
            #bit13 Reserve aktiv
            protection = protection % 2**13
            Fehler_13 = 1
        else:
            Fehler_13 = 0
            
        if protection // 2**12 == 1:
            #bit12 MOS Software Lock in aktiv
            protection = protection % 2**12
            Fehler_12 = 1
        else:
            Fehler_12 = 0
            
        if protection // 2**11 == 1:
            #bit11 Fore end IC Error aktiv
            protection = protection % 2**11
            Fehler_11 = 1
        else:
            Fehler_11 = 0
            
        if protection // 2**10 == 1:
            #bit10 Short Circuit aktiv
            protection = protection % 2**10
            Fehler_10 = 1
        else:
            Fehler_10 = 0
            
            
        if protection // 2**9 == 1:
            #bit9 Discharging Over current aktiv
            self.Error_A6_Strom_entl = 1
            protection = protection % 2**9
        else:
            self.Error_A6_Strom_entl = 0
            
        if protection // 2**8 == 1:
            #bit8 Charging Over current aktiv
            self.Error_A7_Strom_laden = 1
            protection = protection % 2**8
        else:
            self.Error_A7_Strom_laden = 0
        
        if protection // 2**7 == 1:
            #bit7 Discharging Low temp aktiv
            self.Error_A3_Temp_min_entl = 1
            protection = protection % 2**7
        else:
            self.Error_A3_Temp_min_entl = 0
            
        if protection // 2**6 == 1:
            #bit6 Discharging Over temp aktiv
            self.Error_A2_Temp_max_entl = 1
            protection = protection % 2**6
        else:
            self.Error_A2_Temp_max_entl =0
            
        if protection // 2**5 == 1:
            #bit5 Charging Low temp aktiv
            self.Error_A5_Temp_min_laden = 1
            protection = protection % 2**5
        else:
            self.Error_A5_Temp_min_laden = 0
            
        if protection // 2**4 == 1:
            #bit4 Charging Over temp aktiv
            self.Error_A4_Temp_max_laden = 1
            protection = protection % 2**4
        else:
            self.Error_A4_Temp_max_laden = 0
            
        if protection // 2**3 == 1:
            #bit3 Battery Under Vol aktiv
            protection = protection % 2**3
            Fehler_3 = 1
        else:
            Fehler_3 = 0
            
        if protection // 2**2 == 1:
            #bit2 Battery Over Vol aktiv
            protection = protection % 2**2
            Fehler_2 = 1
        else:
            Fehler_2 = 0
            
        if protection // 2**1 == 1:
            #bit1 Cell Block Under Vol aktiv
            self.Error_A1_Zell_min = 1
            protection = protection % 2**1
        else:
            self.Error_A1_Zell_min = 0
            
        if protection // 1 == 1:
            #bit0 Cell Block Over Vol aktiv
            self.Error_A0_Zell_max = 1
            protection = protection % 1
        else:
            self.Error_A0_Zell_max = 0
        

        self.Error_B0_isolation = 0
        self.Error_B1_Comm_Timeout = 0
        
        if (Fehler_15 or Fehler_14 or Fehler_13 or Fehler_12 or Fehler_11 or Fehler_10 or Fehler_3 or Fehler_2) ==1:
            self.Error_B2_Fehler = 1
        else:
            self.Error_B2_Fehler = 0
            
        self.Error_A = self.Error_A7_Strom_laden*2**7 + self.Error_A6_Strom_entl*2**6 + self.Error_A5_Temp_min_laden*2**5 + self.Error_A4_Temp_max_laden*2**4 + self.Error_A3_Temp_min_entl*2**3 + self.Error_A2_Temp_max_entl*2**2 + self.Error_A1_Zell_min*2**1 + self.Error_A0_Zell_max
        
        self.Error_B = self.Error_B7_reserved5*2**7 + self.Error_B6_reserved4*2**6 + self.Error_B5_reserved3*2**5 + self.Error_B4_reserved2*2**4 + self.Error_B3_reserved1*2**3 + self.Error_B2_Fehler*2**2 + self.Error_B1_Comm_Timeout*2**1 + self.Error_B0_isolation
        
    def getErrorA(self):
        return self.Error_A
    def getErrorB(self):
        return self.Error_B
    
    
    def printcodes(self):
        
        print('Status_A0_AUX1 = ', self.Status_A0_AUX1)
        print('Status_A1_AUX2 = ', self.Status_A1_AUX2)
        print('Status_A2_AUX3 = ', self.Status_A2_AUX3)
        print('Status_A3_AUX4 = ', self.Status_A3_AUX4)
        print('Status_A4_P_plus = ', self.Status_A4_P_plus)
        print('Status_A5_C_plus = ',  self.Status_A5_C_plus)
        print('Status_A6_Balancing = ', self.Status_A6_Balancing)
        print('Status_A7_Ladegerät_present = ', self.Status_A7_Ladegerät_present)

        print('Status A: ', bin(self.Status_A), hex(self.Status_A), self.Status_A)

        print('Status_B0_Ladegerät_aktiv = ', self.Status_B0_Ladegerät_aktiv)
        print('Status_B1_Ladevorgang_beendet = ', self.Status_B1_Ladevorgang_beendet)
        print('Status_B2_bereit = ', self.Status_B2_bereit)
        print('Status_B3_reserved1 = ', self.Status_B3_reserved1)
        print('Status_B4_reserved2 = ', self.Status_B4_reserved2)
        print('Status_B5_reserved3 = ', self.Status_B5_reserved3)
        print('Status_B6_reserved4 = ', self.Status_B6_reserved4)
        print('Status_B7_reserved5 = ', self.Status_B7_reserved5)

        print('Status B: ', bin(self.Status_B), hex(self.Status_B), self.Status_B)
        
        '''
        print('Warning_A0_Zell_max = ', self.Warning_A0_Zell_max)
        print('Warning_A1_Zell_min = ', self.Warning_A1_Zell_min)
        print('Warning_A2_Temp_max_entl = ', self.Warning_A2_Temp_max_entl)
        print('Warning_A3_Temp_min_entl = ', self.Warning_A3_Temp_min_entl)
        print('Warning_A4_Temp_max_laden = ', self.Warning_A4_Temp_max_laden)
        print('Warning_A5_Temp_min_laden = ',  self.Warning_A5_Temp_min_laden)
        print('Warning_A6_Strom_entl = ', self.Warning_A6_Strom_entl)
        print('Warning_A7_Strom_laden = ', self.Warning_A7_Strom_laden)
        
        print('Warning A: ', bin(self.Warning_A), hex(self.Warning_A), self.Warning_A)
        
        print('Warning_B0_isolation = ', self.Warning_B0_isolation)
        print('Warning_B1_Akku_disbalance = ', self.Warning_B1_Akku_disbalance)
        print('Warning_B2_SoC_min = ',  self.Warning_B2_SoC_min)
        print('Warning_B3_reserved1 = ', self.Warning_B3_reserved1)
        print('Warning_B4_reserved2 = ', self.Warning_B4_reserved2)
        print('Warning_B5_reserved3 = ', self.Warning_B5_reserved3)
        print('Warning_B6_reserved4 = ', self.Warning_B6_reserved4)
        print('Warning_B7_reserved5 = ', self.Warning_B7_reserved5)
        
        print('Warning B: ', bin(self.Warning_B), hex(self.Warning_B), self.Warning_B)

        
        print('Error_A0_Zell_max = ', self.Error_A0_Zell_max)
        print('Error_A1_Zell_min = ', self.Error_A1_Zell_min)
        print('Error_A2_Temp_max_entl = ', self.Error_A2_Temp_max_entl)
        print('Error_A3_Temp_min_entl = ', self.Error_A3_Temp_min_entl)
        print('Error_A4_Temp_max_laden = ', self.Error_A4_Temp_max_laden)
        print('Error_A5_Temp_min_laden = ',  self.Error_A5_Temp_min_laden)
        print('Error_A6_Strom_entl = ', self.Error_A6_Strom_entl)
        print('Error_A7_Strom_laden = ', self.Error_A7_Strom_laden)
        
        print('Error A: ', bin(self.Error_A), hex(self.Error_A), self.Error_A)
        
        print('Error_B0_isolation = ', self.Error_B0_isolation)
        print('Error_B1_Comm_Timeout = ', self.Error_B1_Comm_Timeout)
        print('Error_B2_Fehler = ', self.Error_B2_Fehler)
        print('Error_B3_reserved1 = ', self.Error_B3_reserved1)
        print('Error_B4_reserved2 = ', self.Error_B4_reserved2)
        print('Error_B5_reserved3 = ', self.Error_B5_reserved3)
        print('Error_B6_reserved4 = ', self.Error_B6_reserved4)
        print('Error_B7_reserved5 = ', self.Error_B7_reserved5)
        
        print('Error B: ', bin(self.Error_B), hex(self.Error_B), self.Error_B)     
        '''