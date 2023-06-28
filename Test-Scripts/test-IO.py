#!/usr/bin/python

########################################################################
# V1.0
########################################################################

from clIO import clIO
import sys 
import getopt
import time

io = clIO()


def main(argv):
    
    sFlag=False
    rnum=0
    rsw=0
    switch=""
    rrr=0
    try:
      opts, args = getopt.getopt(argv,"h:r:s:d:g:",["help=", "relais=","switch=","demo","get="])

    except getopt.error as msg:
        print("--demo ")
        print("--relais <Relais Nummer> --switch <on|off>")
        print("--get <Relais Nummer>")
        sys.exit(2)


    for opt, arg in opts:
        if opt in ( '-h',"--help"):
            print("-r <Relais Nummer> -s <on|off> -d -g <Relais Nummer>")
            print("-relais <Relais Nummer> -switch <on|off> --demo --get <Relais Nummer>")
            sys.exit()
        elif opt in ("-r", "--relais"):
            rnum=int(arg)

        elif opt in ("-s", "--switch"):
            switch=arg
            sFlag=True
        elif opt in ("-d", "--demo"):
            print("Demo")
            io.Demo()
        elif opt in ("-g", "--get"):
            rrr=io.GetRelay( int(arg) )
            print("Relai Nr: ", int(arg),  "Status: ", rrr )
            
 
    if sFlag:   #wenn switch paramter übergeben wurde relais schalten
      if switch == "on":
        rsw=1
      else: 
        rsw=0

      io.SetRelay(rnum,rsw)
      print("Relai Nr: ",rnum,switch, rsw)
        
if __name__ == "__main__":
   main(sys.argv[1:])
