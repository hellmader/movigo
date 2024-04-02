#!/usr/bin/python

########################################################################
# V1.0
########################################################################


from smartBMS import Request, smartBMS
from dataprocess import dataprocessing
import time
import threading
from multiprocessing import Queue
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
import configparser
import configparser

config = configparser.ConfigParser()
config.read("/home/hell/sw/etc/bms.config")


TBServer  = config['thingsboard']['Server']
TBToken  = config['thingsboard']['Token']
TBAkku  = config['thingsboard']['Akku']




toBmsQueue = Queue()
fromBmsQueue = Queue()

qDatafromBMS = 0
Data={}
client = TBDeviceMqttClient( host=TBServer, token=TBToken, port=1883 )

try:
    #https://github.com/thingsboard/thingsboard-python-client-sdk/blob/master/tb_device_mqtt.py
    #https://thingsboard.io/docs/pe/reference/python-client-sdk/
    print("111")
    client.connect()
    client.max_queued_messages_set(1)
    client.reconnect_delay_set(5,5)
    
    print("222")
except:
    print("keine Verbindung zu TB")
    pass


Starttime = int(round(time.time() * 1000))
if __name__ == '__main__':
    threads = []
    sendReq = 0

    bms = smartBMS(0,1000, toBmsQueue, fromBmsQueue)
    bms.start()

    
    
    dataproc = dataprocessing()


    time.sleep(.1)

    t = int(round(time.time() * 1000))
    updateTimeStart_dataprocessing = int(round(time.time() * 1000))
    updateTimeStart_thingsboard = int(round(time.time() * 1000))
    
    try:
        while(1):
            
            
            try:
                qDatafromBMS = fromBmsQueue.get_nowait()
                if (qDatafromBMS):
                    #print(qDatafromBMS)
                    dataproc.updateBMS(qDatafromBMS)
                    print('BMS Daten geladen')
            except:
                # do nothing
                pass
            

            if (int(round(time.time() * 1000)) - updateTimeStart_dataprocessing) >250: # every 250ms   
                updateTimeStart_dataprocessing = int(round(time.time() * 1000))
                # jede x millisekunde werden die error codes und status bits neu berechnet
                
                
                BMS_Data = dataproc.getBMSdata()
                #print('BMS Data: ',BMS_Data)
                Data=BMS_Data
            

            
                
            #Daten an Thingsboard
            if (int(round(time.time() * 1000)) - updateTimeStart_thingsboard)>5000: # every 5000ms
                updateTimeStart_thingsboard = int(round(time.time() * 1000))                 
                Data.update({'Akkuname': TBAkku})

                client.send_telemetry(Data)
                print("############################################")
                print("Thingsboard upload")
                print("############################################")
                



            time.sleep(.1)
    
        
    except KeyboardInterrupt:
        toBmsQueue.put("SIG-INT")
        
        print("wait for threads to join")
        bms.join()
        print("threads successfully closed")
    


