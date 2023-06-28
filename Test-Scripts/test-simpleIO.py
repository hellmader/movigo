
import smbus
import sys
import time
from Adafruit_I2C import Adafruit_I2C
from MCP230xx import Adafruit_MCP230XX as MCP230xx

mcp = MCP230xx(busnum=1 , address = 0x20, num_gpios = 8) # MCP23008



# Set pins  to output 

#bei configuration setzen werden die relais geschalten
mcp.config(0, mcp.OUTPUT)
mcp.config(1, mcp.OUTPUT)
mcp.config(2, mcp.OUTPUT)
mcp.config(3, mcp.OUTPUT)

mcp.config(4, mcp.INPUT)
mcp.config(5, mcp.INPUT)
mcp.config(6, mcp.INPUT)
mcp.config(7, mcp.INPUT)



while True:
  print("Relai 4 off")
  mcp.output(3,0)
  time.sleep(5)
  print("input 7:",mcp.input(7)  )
  time.sleep(5)
  
  print("Relai 4 on")
  mcp.output(3,1)
  time.sleep(5)
  print("input 7:",mcp.input(7)  )
  time.sleep(5)



x=3
#turn on pins
if x==1:
  print("run 1")
  mcp.output(0,1)
  mcp.output(1,1)
  mcp.output(2,1)
  mcp.output(3,1)

#turn off pins
if x==2:
  print("run 2")
  mcp.output(0,0)
  mcp.output(1,0)
  mcp.output(2,0)
  mcp.output(3,0)

if x==3:
  print( "run3")






