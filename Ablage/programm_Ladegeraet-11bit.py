#!/usr/bin/python

########################################################################
# V1.0
########################################################################

import serial
import time
import threading
import enum
import can
import logging
from clHelper import checkTime


class Request(enum.Enum):
    NONE = 0
    BASIC_INFO = 1
    CELL_VOLTAGE = 2


def current_milli_time():
    return round(time.time() * 1000)

class Ladegeraet(threading.Thread):
    def __init__(self, debugOutput, updateCycle, outCANfromLadegeraet, inCANtoLadegeraet):
        threading.Thread.__init__(self)
        self.debugOutput = debugOutput
        self.updateCycle = updateCycle
        self.outCANfromLadegeraet = outCANfromLadegeraet
        self.inCANtoLadegeraet = inCANtoLadegeraet

        
        self.readCANfromLadegeraet = None
        CAN_filter = [{"can_id": 0x112 , "can_mask": 0x7FF, "extended": False}]
        self.readcan = can.interface.Bus(channel = 'can0', bustype = 'socketcan', bitrate=500000, can_filters = CAN_filter)
        #self.readcan = can.interface.Bus(channel = 'can0', bustype = 'socketcan', bitrate=500000, can_filters = [{"can_id": 0x112 , "can_mask": 0x7FF, "extended": False}])
        #self.readcan = can.interface.Bus(channel = 'can0', bustype = 'socketcan', bitrate=500000, can_filters = [{"can_id": 0x18FF50E5 , "can_mask": 0x18FF50E5, "extended": True}])
        self.Spannung_Ladegeraet = 0
        self.Strom_Ladegeraet = 0
        self.Status_Ladegeraet = None
        
        self.writecan = can.interface.Bus(channel = 'can0', bustype = 'socketcan', bitrate=500000)
        self.Ladeschlussspannung = 29.4*10
        self.Ladestrom = 100*10#500
        self.Regler = 0 #0: Charger start charging, 1: Battery protection Charger Stop Output, 2: Heating mode
        self.SoC = 0
        

    
    def readLadegeraet(self,msg):

        #ladegeraet vorhanden, sende Ladegeraete daten in die Warteschlange
        msg = self.readcan.recv(2)
        print(msg)
        #if msg == None:
        #  self.readCANfromLadegeraet = None
          #print("kein CAN Ladegerät ")

        #elif str(hex(msg.arbitration_id))=='0x18ff50e5':
            #print("ladegeraet vorhanden")
        self.Spannung_Ladegeraet = int.from_bytes(msg.data[0:2], 'big') # 531 bedeutet 53,1V
        self.Strom_Ladegeraet = int.from_bytes(msg.data[2:4], 'big') # 280 bedeutet 28A
        self.Status_Ladegeraet = int.from_bytes(msg.data[4:5], 'big')
        if (self.Status_Ladegeraet <32) or (self.Status_Ladegeraet == 0):
                self.readCANfromLadegeraet = {'Ladegeraet Spannung': self.Spannung_Ladegeraet, 'Ladegeraet Strom': self.Strom_Ladegeraet, 'Ladegeraet Status': self.Status_Ladegeraet}
        logging.info('Ladegerät gefunden')
            
        #else:
        #    self.readCANfromLadegeraet = None

        self.outCANfromLadegeraet.put(self.readCANfromLadegeraet)
        time.sleep(0.01)
        
        
        
    def readLadegeraetprint(self):
                
        logging.info('Spannung: {}'.format(self.Spannung_Ladegeraet) )
        logging.info ('Strom: {}'.format ( self.Strom_Ladegeraet) )
        logging.info("Status: {}".format( bin(self.Status_Ladegeraet)) )
        print('22222')
        #Bit0 Hardware Error 0: normal. 1: Hardware error
        if bin(self.Status_Ladegeraet>>0)[-1]=='0':
            logging.info('Bit0 = 0 -> normal')
        else:
            logging.info('Bit0 = 1 -> Harware error')
        #Bit1 Charger Temperature 0: normal. 1: Charger over temperature protection
        if bin(self.Status_Ladegeraet>>1)[-1]=='0':
            logging.info('Bit1 = 0 -> normal')
        else:
            logging.info('Bit1 = 1 -> Charger over temperature protection')
        #Bit2 Input Voltage 0: Input voltage normal. 1: Input voltage is wrong and the charger stops working
        if bin(self.Status_Ladegeraet>>2)[-1]=='0':
            logging.info('Bit2 = 0 -> Input voltage normal')
        else:
            logging.info('Bit2 = 1 -> Input voltage is wrong and the charger stops working')
        #Bit3 Start state 0: the charger detects that the battery voltage enters the start state. 1: Is off. (used to prevent reverse connection of battery)
        if bin(self.Status_Ladegeraet>>3)[-1]=='0':
            logging.info('Bit3 = 0 -> the charger detects that the battery voltage enters the start state')
        else:
            logging.info('Bit3 = 1 -> Is off. (used to prevent reverse connection of battery)')
        #Bit4 Communication status 0: communication is normal. 1: Communication receiving timeout
        if bin(self.Status_Ladegeraet>>4)[-1]=='0':
            logging.info('Bit4 = 0 -> communication is normal')
        else:
            logging.info('Bit4 = 1 -> Communication receiving timeout')
    
    def writeLadegeraet(self, data):
        #print(data)
        self.SoC = data['SoC']
        self.Regler = data['Regler']
        self.maxSpannung = data['maximale Zellspannung']
        self.minSpannung = data['minimale Zellspannung']
        self.Spannung = data['Spannung']
        self.maxTemp = max(data['Temperatur 1'],data['Temperatur 2'])
        if self.SoC ==0:
            self.SoC = 1
        logging.info('Regler = {}'.format(self.Regler) )
        print('1111111111111111111111111111111111')
        data_Ladegeraet_1 =int(self.Ladeschlussspannung).to_bytes(2, 'big') + int(self.Ladestrom).to_bytes(2, 'big') + int(self.Regler).to_bytes(1, 'big') + int(0).to_bytes(3, 'big')
        msg_1 = can.Message(data=data_Ladegeraet_1, arbitration_id=0x111, is_extended_id=False)
        print('222222222222222222222222222222222222')
        data_Ladegeraet_2 =int(self.maxSpannung*1000).to_bytes(2, 'big') + int(self.minSpannung*1000).to_bytes(2, 'big') + int(self.SoC).to_bytes(1, 'big') + int(self.maxTemp+40).to_bytes(1, 'big') + int(self.Spannung*10).to_bytes(2, 'big')
        msg_2 = can.Message(data=data_Ladegeraet_2, arbitration_id=0x115, is_extended_id=False)
        print('----------------------------')
        #logging.info(msg1)
        #logging.info(msg2)
        print(msg_1)
        print(msg_2)
        print('--------------------------------------------------')
        self.writecan.send(msg_1)
        self.writecan.send(msg_2)
        

        
    def run(self):
        if self.debugOutput:
            print("can: Run - Start Thread")
        incData = []
        self.running = True

        t1 = checkTime() 
        FlagCharger = False
        FlagChargerTimeout=True

        while(self.running):
            time.sleep(.01)   #wichtig sonst 100% cpu auslastung
            #check for incoming data from main thread

            try:
                msg = self.readcan.recv(0)  #lese cannachrichten  ohne timeout fuer ladegeraet ein
                #print('MSG',msg)
                try:
                    if str(hex(msg.arbitration_id))=='0x112':  # pruefe auf ladegerate adresse nur Ladegerate id
                        FlagCharger = True  #Ladegeraet vorhanden
                        FlagChargerTimeout = False   #setze flag wenn Ladegeraet id vorhanden ist
                        sendmsg=msg
                        print("Ladegeraet ist daaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa ")
                        self.readLadegeraet(sendmsg)
                        self.readLadegeraetprint()
                    else:
                        print("kein ladegeraettttttttttttttttttttttttttttttttttttttttttttttttt")
                except:
                    #print('Exception 2')
                    pass
              
                if FlagCharger == True: #starte timer wen ladegaerate da ist
                    if t1.getTime(7000):
                        print("alle 3 sekunden nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn")     

                        if FlagChargerTimeout==True:  ##ladegaeraet abgesteckt
                            print("Ladegeraet ausssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss")
                            self.readCANfromLadegeraet = None  #meldung an dataprocess
                            self.outCANfromLadegeraet.put(self.readCANfromLadegeraet)
                            FlagCharger = False   #charger ist weg
                            FlagChargerTimeout= True  #doppelt gemoppelt

                        FlagChargerTimeout = True  # zum erneuten pruefen abstellen, dadurch lauft ladegerat erkennung´ins timeout                
            except:
                print('Exception First Try')
                pass

            
            try:
                qDataIn = self.inCANtoLadegeraet.get_nowait()
                self.writeLadegeraet(qDataIn)

                #time.sleep(1)
            except:
                # do nothing
                pass

        if self.debugOutput:
                print("canO: Thread exit")
                        



