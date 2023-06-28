import serial
import time
from clHelper import checkTime
from clIO import clIO
import os
import can


io = clIO()
t1 = checkTime()


def service(cmd):
  #stop all service
  print("Beende Service:  bms, canopen, profinet")
  print("")
  
  if cmd == "stop":
    os.system("sudo systemctl stop bms")
    os.system("sudo systemctl stop canopen")
    os.system("sudo systemctl stop profinet")

  if cmd == "start":
    os.system("sudo systemctl stop bms")
    os.system("sudo systemctl stop canopen")
    os.system("sudo systemctl stop profinet")


def checkBMS():
  # check BMS
  # Get Hardware Info
  serialBMS = serial.Serial()
  serialBMS.baudrate = 9600
  serialBMS.port = '/dev/ttyS2'
  serialBMS.timeout = 0.2
  serialBMS.open()

  basicBMS = [0xDD, 0xA5, 0x05, 0x00, 0xFF, 0xFB, 0x77]

  print("###################################")
  print("")
  print("Pruefe BMS...")
  print("")
  print("###################################")
  print("")

  bmsFlag=True
  bmsCount=0
  while bmsFlag:
    time.sleep(.01) #CPU
    serialBMS.write(basicBMS) 
    ret = serialBMS.read(200)
    if ret:
      try: 
        if ret[1] == 5 and ret[2] == 0 :
          print("")
          print("Bms Verbindung ok")
          print("")
          bmsFlag=False

      except:
        print("timeout BMS ")
        print("pruefe BMS nochmals...")

    bmsCount=bmsCount+1
    print(bmsCount,sep='',end=' ',flush=True)
    time.sleep(.5)

    if bmsCount > 10:
      print("")
      print("KEINE Bms Verbindung")
      bmsFlag=False

def checkCAN():
  print("###################################")
  print("")
  print("Pruefe CAN...")
  print("")
  print("###################################")
  print("")

  #Testadresse isendet folgende ID und daten: 0x12345678 mit Daten 00 11 22 33 44 55 66 77 (Hex value)
  CAN_filter = [{"can_id": 0x12345678 , "can_mask": 0x12345678, "extended": True}]
  can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan', can_filters = CAN_filter)


  CANFlag=True
  CANcount=0
  print("CAN Test: ")
  while CANFlag:
    message = can0.recv(.1) #time 100ms

    try:
      time.sleep(.01) #cpu friendly

      #pruefe id und daten
      if message.arbitration_id == 0x12345678:
        if message.data[1] == 0x11 and message.data[2] == 0x22:
          print("")
          print("CAN Verbindung OK")
          print("")
          CANFlag=False
    except:
      pass

    CANcount=CANcount+1
    print(CANcount,sep='',end=' ',flush=True)
    time.sleep(.5)
    if CANcount > 10:
      print("")
      print("KEINE CAN Verbindung")
      print("")
      CANFlag=False


def checkRELAIS(nr,relais):

  if nr==1:
    print("###################################")
    print("")
    print("Pruefe Relais...")
    print("")
    print("###################################")
    print("")
    print("Schalte alle Relais ab")
    io.SetRelay(1,0)
    io.SetRelay(2,0)
    io.SetRelay(3,0)
    io.SetRelay(4,0)
    input("Eingabe Taste druecken")

  if nr==2:
    print(" ")
    print("Schalte Relais Nr:  ein",relais)
    io.SetRelay(relais,1)
    input("Eingabe Taste druecken")

    print(" ")
    print("Schalte Relais Nr:  aus",relais)
    io.SetRelay(relais,0)
    input("Eingabe Taste druecken")




service("stop")

checkBMS()  
input("Eingabe Taste druecken")

checkCAN()  
input("Eingabe Taste druecken")

checkRELAIS(1,0) #alle relais aus

checkRELAIS(2,1) 

checkRELAIS(2,2) 

checkRELAIS(2,3) 

checkRELAIS(2,4) 
