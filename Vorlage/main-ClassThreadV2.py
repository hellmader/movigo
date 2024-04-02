# -*- coding: utf-8 -*-
"""
Created on Fri Jun  3 07:19:46 2022

@author: produktion
"""



from ClassThreadV2 import UDP
import threading
from multiprocessing import Queue
import time

toUDPQueue = Queue()
fromUDPQueue = Queue()

i=0

if __name__ == '__main__':
    
    UDP = UDP(0,1000,toUDPQueue, fromUDPQueue)
    UDP.start()
    
    updateTimeStart = int(round(time.time() * 1000))
    
    try:
        while(1):
            try:
                qfromUDP = fromUDPQueue.get_nowait()
                print('Data from UDP:   ',qfromUDP)

            except:
                pass
            if (int(round(time.time() * 1000)) - updateTimeStart) >3000: # every 5000ms 
                updateTimeStart = int(round(time.time() * 1000))
                i=i+0.1
                data = {'Spannung': 45.9+i, 'Strom': 0, 'SoC': 100, 'Temperatur 1': 24.2, 'Temperatur 2': 25.1, 'Temperatur 3': 23.4, 'Temperatur 4': -273.15, 'maximale Zellspannung': 3.534, 'Position maximale Zellspannung': 10, 'minimale Zellspannung': 3.526, 'Position minimale Zellspannung': 5, 'Isolationswiderstand Gehäuse gegen PLUS': 38, 'Isolationswiderstand Gehäuse gegen MINUS': 38, 'spezifischer Isolationswiderstand Gehäuse gegen PLUS': 50, 'spezifischer Isolationswiderstand Gehäuse gegen MINUS': 50, 'Protection Status': 0, 'Balance Status': 0, 'Anzahl der Seriell-Verbindungen': 13, 'maximal erlaubte Zellspannung': 4.25, 'minimal erlaubte Zellspannung': 2.7, 'maximal erlaubte Batteriespannung': 55.25, 'minimal erlaubte Batteriespannung': 35.1, 'maximaler Entladestrom': 60, 'maximaler Ladestrom': 60, 'Minimale Temperatur Laden': 5, 'Maximale Temperatur Laden': 60, 'Minimale Temperatur Entladen': 0, 'Maximale Temperatur Entladen': 65, 'Fehlerauslösezeit': 5, 'nominelle Spannung': 48.1, 'nominelle Kapazität': 52.0, 'nominelle Energie': 2501.2000000000003, 'StatusA': 1, 'StatusB': 4, 'WarningA': 0, 'WarningB': 0, 'ErrorA': 0, 'ErrorB': 0}

                toUDPQueue.put(data)
            time.sleep(0.01)

    except KeyboardInterrupt:
        toUDPQueue.put("SIG-INT")
        
        print("wait for threads to join")
        UDP.join()

        print("threads successfully closed")
    