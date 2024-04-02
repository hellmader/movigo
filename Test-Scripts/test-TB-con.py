#!/usr/bin/python

########################################################################
# V1.0
########################################################################


from smartBMS import Request, smartBMS
import time
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
import configparser
import threading

config = configparser.ConfigParser()
config.read("/home/hell/sw/etc/bms.config")


TBServer  = config['thingsboard']['Server']
TBToken  = config['thingsboard']['Token']
TBAkku  = config['thingsboard']['Akku']


def thread_TB():
  client2 = TBDeviceMqttClient( host=TBServer, token=TBToken, port=1883 )

  while True:
    time.sleep(2)
    print("Verbindungs beginn")

    if client2.is_connected() == False:
      print("")
      print("Verbindungsaufbau...")
      try: 
        ret=client2.connect()
        print("Returncode:")
        print("ret")
        print("Verbindungsaufbau erfolgreich")
        time.sleep(3)
      except:
        print("Verbindungsaufbau fehler")

    else:
      print("sende Daten zu TB")
      client2.send_telemetry({"test":time.time() })






client = TBDeviceMqttClient( host=TBServer, token=TBToken, port=1883 )

x = threading.Thread(target=thread_TB  )
x.start()



while True:



  '''
  #1 direkter aufruf Verbindung im main Programm
  try:
    #https://github.com/thingsboard/thingsboard-python-client-sdk/blob/master/tb_device_mqtt.py
    #https://thingsboard.io/docs/pe/reference/python-client-sdk/
    print("Verbindungs beginn")
    if client.is_connected() == False:
      print("Verbindungsaufbau...")
      client.max_queued_messages_set(1)
      client.reconnect_delay_set(5,5)
      client.connect()
      print("Verbindungsaufbau erfolgreich")
    else:
      print("sende Daten zu TB")
      client.send_telemetry({"test":time.time() })

  except:
    print("keine Verbindung zu TB")
  '''

  print("")
  print("Restliches Programm wird ausgefuehrt")
  time.sleep(5)




