"""
Created on Sat Jun 17 15:44:28 2023

@author: cschi

!!! Nicht getestet!!!



#Abruf der Daten im Main per
system_parameter = ueberwache_system()
print(system_parameter)
"""
import psutil
def rTemp(tempsensor):
  try:
    f = open(tempsensor,'r')
    tempvalue=f.readline()
    f.close
  except:
    tempvalue=0
  return(tempvalue)
def ueberwache_system():
    system_info = {}

    # CPU-Auslastung
    cpu_prozent = psutil.cpu_percent()
    system_info["CPU-Auslastung"] = f"{cpu_prozent}%"
    
    # Speicherauslastung
    virtueller_speicher = psutil.virtual_memory().percent
    system_info["Speicherauslastung"] = f"{virtueller_speicher}%"
    
    # Festplattenbelegung
    festplatten = psutil.disk_usage('/')
    system_info["Festplattenbelegung"] = f"{festplatten.percent}%"
    
    # Netzwerkauslastung
    netzwerk_stats = psutil.net_io_counters()
    netzwerk_auslastung = netzwerk_stats.bytes_sent + netzwerk_stats.bytes_recv
    system_info["Netzwerkauslastung"] = f"{netzwerk_auslastung} Bytes"
    
    # Temperaturinformationen
    temperatur_info= int(rTemp("/sys/class/thermal/thermal_zone0/temp"))/1000
    system_info["Temperatur 8"] = temperatur_info
    system_info["CPUTemp"] = temperatur_info
    
    # Netzwerkverbindungen
    #netzwerk_verbindungen = psutil.net_connections()
    #system_info["Netzwerkverbindungen"] = netzwerk_verbindungen
    
    # Laufende Prozesse
    #laufende_prozesse = psutil.process_iter()
    #system_info["Laufende Prozesse"] = laufende_prozesse
    
    # Systemlast
    systemlast = psutil.getloadavg()
    system_info["Systemlast"] = str(systemlast)

    return system_info
