#!/usr/bin/python

########################################################################
# V1.0
########################################################################

import time
import threading
import enum
import can
import logging
import configparser

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
        
        config = configparser.ConfigParser()
        config.read("/home/hell/sw/etc/bms.config")
        TBAkku  = config['thingsboard']['Akku']
        TBSN  = config['thingsboard']['Seriennummer']
        APP_Mode=TBSN[:4]
        TuenkersPROFI_ID=["3042","3419"]
        TuenkersCAN_ID=["3212","3222","2455","3470"]
        if APP_Mode in(TuenkersPROFI_ID):
            baudrate=250000
        elif APP_Mode in(TuenkersCAN_ID):
            baudrate=500000
        
        self.readCANfromLadegeraet = None
        self.readcan = can.interface.Bus(channel = 'can0', bustype = 'socketcan', bitrate=baudrate, can_filters = [{"can_id": 0x18FF50E5 , "can_mask": 0x1FFFFFFF, "extended": True}])
        self.Spannung_Ladegeraet = 0
        self.Strom_Ladegeraet = 0
        self.Status_Ladegeraet = None
        
        self.writecan = can.interface.Bus(channel = 'can0', bustype = 'socketcan', bitrate=baudrate)
        self.Ladeschlussspannung = 54.6*10
        self.Ladestrom = 50*10 #500
        self.Regler = 0 #0: Charger start charging, 1: Battery protection Charger Stop Output, 2: Heating mode
        self.SoC = 0
        self.none_count = 0
        self.time_last_msg = None
        self.time_first_msg= None
        self.Flag = False

    
    def readLadegeraet(self):
        msg = self.readcan.recv(2)
        #logging.info(msg)
        
        if msg is None:
            self.none_count += 1
            if self.none_count >= 5:
                self.time_last_msg = time.time()
                self.none_count = 0
            if (time.time() - self.time_last_msg<= 5):
                pass
            elif (time.time()-self.time_first_msg>= 5):
                self.readCANfromLadegeraet = None
            
        else:
            if self.Flag ==True:
                self.time_first_msg=time.time()
                self.Flag = False
            if time.time()-self.time_first_msg >=5:
               
                self.Spannung_Ladegeraet = int.from_bytes(msg.data[0:2], 'big') # 531 bedeutet 53,1V
                self.Strom_Ladegeraet = int.from_bytes(msg.data[2:4], 'big') # 280 bedeutet 28A
                self.Status_Ladegeraet = int.from_bytes(msg.data[4:5], 'big')
                if (self.Status_Ladegeraet <32) or (self.Status_Ladegeraet == 0):
                    self.readCANfromLadegeraet = {'Ladegeraet Spannung': self.Spannung_Ladegeraet, 'Ladegeraet Strom': self.Strom_Ladegeraet, 'Ladegeraet Status': self.Status_Ladegeraet,'Ladegeraet Present': True}
                #logging.info('Ladegerät gefunden')
            else:
                self.readCANfromLadegeraet = None
            self.time_last_msg = time.time()
            
        if(time.time()-self.time_last_msg>= 5):
            self.readCANfromLadegeraet = None
            self.Flag = True
            
        self.outCANfromLadegeraet.put(self.readCANfromLadegeraet)
        time.sleep(0.01)
        
        
        
    def readLadegeraetprint(self):
                
        logging.info('Spannung: {}'.format(self.Spannung_Ladegeraet) )
        logging.info ('Strom: {}'.format ( self.Strom_Ladegeraet) )
        logging.info("Status: {}".format( bin(self.Status_Ladegeraet)) )
        
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
        
        self.Ladeschlussspannung = data['Ladeschlussspannung']
        self.Ladestrom = data['Ladestrom']
        self.SoC = data['SoC']
        try:
            self.tcharge=data['tcharge']
        except KeyError:  # Default value for variable2 when variable1 doesn't exist
            self.tcharge=1
        
     
        if data['CPUTemp']>80:
            self.scharge=0.2
        else:
            self.scharge=1
        if self.SoC ==0:
            self.SoC = 1
        logging.info('Regler = {}'.format(self.Regler) )
        self.Laderate=self.tcharge*self.scharge
        if(data['StatusLaden']==True) and  (data['StatusLadenEnde']==False):
            self.Regler=0
        else:
            self.Regler=1
        data_Ladegeraet =int(self.Ladeschlussspannung*10).to_bytes(2, 'big') + int(self.Ladestrom*self.Laderate*10).to_bytes(2, 'big') + int(self.Regler).to_bytes(1, 'big') + int(self.SoC).to_bytes(1, 'big') + int(0).to_bytes(2, 'big')
        msg = can.Message(data=data_Ladegeraet, arbitration_id=0X1806E5F4, is_extended_id=True)
       
        logging.info(msg)
        self.writecan.send(msg)
        

        
    def run(self):
        if self.debugOutput:
            print("can: Run - Start Thread")
        incData = []
        self.running = True
        self.time_last_msg=time.time()
        self.time_first_msg= time.time()
        while(self.running):
            time.sleep(.01)   #wichtig sonst 100% cpu auslastung
            #check for incoming data from main thread
            #print('LAAAADEEEENNN')
            try:
                #print(time.time()-self.time_last_msg)
                self.readLadegeraet()
                #self.readLadegeraetprint()
            except:
                # do nothing
                pass
            
            # try:
                # #qDataIn = self.inCANtoLadegeraet.get_nowait()
                # #print(qDataIn)
                # #self.writeLadegeraet(qDataIn)
                
                

                # #time.sleep(1)
            # except:
                # # do nothing
                # pass

        if self.debugOutput:
                print("canO: Thread exit")
                        



