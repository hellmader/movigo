import serial
import time
from clHelper import checkTime


t1 = checkTime()

serialBMS = serial.Serial()
serialBMS.baudrate = 9600
#serialBMS.port = '/dev/ttyUSB1'
serialBMS.port = '/dev/ttyS2'
serialBMS.timeout = 0
serialBMS.open()







'''
data=[18,42]
print(data[0])
print(data[1])

total_voltage = data[0]<<8 | data[1]
print(total_voltage)
exit()
'''


# '0xdd 0xa5 0x3 0x0 0xff 0xfd 0x77
# b'\xdd\xa5\x03\x00\xff\xfdw')
basicBMS = b'\xdd\xa5\x03\x00\xff\x77\xfdw'

basicBMS = bytearray([0xdd, 0xa5,0x03,0x00,0xff,0x77,0xfd])

basicBMS = bytes.fromhex('dd a5 03 00 ff fd 77')
print("BMS:data", basicBMS)


serialBMS.write(basicBMS)    

while True:
    
    if t1.getTime(1000):
        print("Write BMS Data", basicBMS)
        serialBMS.write(basicBMS) 
        
    ret = serialBMS.read(200)
    if ret:
        print("Serial Return:", ret)




