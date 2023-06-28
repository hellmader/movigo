#!/usr/bin/python

########################################################################
# V1.0
########################################################################


import time
import threading
import enum
import logging
from clHelper import checkTime
import pandas as pd
import time, sys
from datetime import datetime

class Request(enum.Enum):
    NONE = 0
    BASIC_INFO = 1
    CELL_VOLTAGE = 2


def current_milli_time():
    return round(time.time() * 1000)

class write_csv (threading.Thread):
    def __init__(self, debugOutput, updateCycle, write_to_csv):
        threading.Thread.__init__(self)
        self.debugOutput = debugOutput
        self.updateCycle = updateCycle
        self.write_to_csv = write_to_csv
        self.hour = datetime.now().strftime("%H:%M:%S")[:2]
        self.path1_pkl =r'/home/hell/logging_csv/data1_' + self.hour + '.csv'
        self.path2_pkl =r'/home/hell/logging_csv/data2_' + self.hour + '.csv'

        
        data = {'Spannung': 0.0, 'Strom': 0.0, 'SoC': 0, 'Temperatur 1': -273.15, 'Temperatur 2': -273.15, 'Temperatur 3': -273.15, 'Temperatur 4': -273.15, 'Temperatur 5': -273.15, 'Temperatur 6': -273.15, 'Temperatur 7': -273.15, 'Temperatur 8': '62916\n'}#, 'maximale Zellspannung': 5.0, 'Position maximale Zellspannung': 0, 'minimale Zellspannung': 0.0, 'Position minimale Zellspannung': 0, 'Isolationswiderstand Gehäuse gegen PLUS': 38, 'Isolationswiderstand Gehäuse gegen MINUS': 38, 'spezifischer Isolationswiderstand Gehäuse gegen PLUS': 50, 'spezifischer Isolationswiderstand Gehäuse gegen MINUS': 50, 'Protection Status': 0, 'Balance Status': 0, 'Anzahl der Seriell-Verbindungen': 0, 'maximal erlaubte Zellspannung': 4.25, 'minimal erlaubte Zellspannung': 2.7, 'maximal erlaubte Batteriespannung': 0.0, 'minimal erlaubte Batteriespannung': 0.0, 'maximaler Entladestrom': 100, 'maximaler Ladestrom': 100, 'Minimale Temperatur Laden': 5, 'Maximale Temperatur Laden': 60, 'Minimale Temperatur Entladen': 0, 'Maximale Temperatur Entladen': 65, 'Fehlerauslösezeit': 5, 'nominelle Spannung': 0.0, 'nominelle Kapazität': 0.0, 'nominelle Energie': 0.0, 'Ladeschlussspannung': 0.0, 'Ladestrom': 0, 'StatusA': 1, 'StatusB': 4, 'WarningA': 3, 'WarningB': 6, 'ErrorA': 0, 'ErrorB': 0, 'Status_AUX1': 1, 'Request_AUX2': 0, 'Request_AUX3': 0, 'Request_AUX4': 0, 'Request_P': 0, 'Request_C': 0, 'Request_sleep': 0, 'TBSN': 'Teststation1', 'Akkuname': 'Teststation1', 'SerienNummer': 'Teststation1', 'Zeit': '18.03.2023 17:01:24', 'CPUTemp': '62916\n', '0x1A8': 0, 'time 0x1A8': 4.031507968902588, '0x2A8': 0, 'time 0x2A8': 4.031519651412964, '0x3A8': 0, 'time 0x3A8': 4.031525373458862, '0x4A8': 0, 'time 0x4A8': 4.031532287597656, '0x228': 0, 'time 0x228': 4.031538724899292, '0x18FF50E5': '0x18000000', 'time 0x18ff50e5': 0.09571433067321777, '0x1806E5F4': 0, 'time 0x1806E5F4': 4.031560659408569, 'Durchlaufzeit': 0.24444842338562012}

        
        df = pd.DataFrame.from_dict(data.items())
        df = df.T # or df1.transpose()
        df.rename(columns=df.iloc[0], inplace = True)
        df.drop([0], inplace = True)
        df_new = df
        
        
        try: 
            df_new_1 = pd.read_csv(self.path1_pkl)#, compression='zip')
            print(df_new_1)
        except:
            df_new_1= pd.DataFrame()
            print('Problem 1')
        try:
            df_new_2 = pd.read_csv(self.path2_pkl)#, compression='zip')
            print(df_new_2)
        except:
            df_new_2= pd.DataFrame()
            print('Problem 2')
        if len(df_new_1)>= len(df_new_2):
            self.df_new = df_new_1
        else:
            self.df_new = df_new_2
        #print('000000000000000000000000000000000000000')
        #print(df_new)
        self.start_test_time = time.time()


    def write(self, data):
        #print (data)
       
        
        
        df = pd.DataFrame.from_dict(data.items())
        df = df.T # or df1.transpose()
        df.rename(columns=df.iloc[0], inplace = True)
        df.drop([0], inplace = True)
        #print('Hallllllllllllllllllllloooooooooooooooooo')
        #print(list(df.columns))
        
        #print(df['Zeit'])
        #print(str(df['Zeit'])[16:18])
        Stunden_Zeit = str(df['Zeit'])[16:18]
        self.path1_pkl =r'/home/hell/logging_csv/data1_' + Stunden_Zeit + '.csv'
        self.path2_pkl =r'/home/hell/logging_csv/data2_' + Stunden_Zeit + '.csv'
        
        if Stunden_Zeit != self.hour:
            self.df_new = df
            self.df_new.to_csv(self.path1_pkl)#, compression='zip')
            self.df_new.to_csv(self.path2_pkl)#, compression='zip')     
        else:
            #self.df_new = pd.concat([self.df_new, df], ignore_index=True, sort=False)
            df.to_csv(self.path1_pkl,mode='a',header=False, index=False)#, compression='zip')
            df.to_csv(self.path2_pkl,mode='a',header=False, index=False)#, compression='zip')    
        self.hour = str(df['Zeit'])[16:18]
        #print(self.hour)
        
       
        
        
        

        
        
        
        #print('5555555555555555555555555555555555555555')
        
        #print('Zeit Datensicherung', self.start_test_time - time.time())
        self.start_test_time = time.time()
        Zahl = 0
        
        #print(len(self.df_new))

            
              
        

        
    def run(self):
        if self.debugOutput:
            print("can: Run - Start Thread")
        incData = []
        self.running = True

        t1 = checkTime() 


        while(self.running):
            time.sleep(.01)   #wichtig sonst 100% cpu auslastung
            #check for incoming data from main thread
            try:
                qDataIn = self.write_to_csv.get_nowait()
                self.write(qDataIn)
                
                #time.sleep(1)
            except:
                # do nothing
                pass

        if self.debugOutput:
                print("canO: Thread exit")
                        



