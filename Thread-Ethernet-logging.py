"""
Created on Sat Jun 17 15:09:16 2023

@author: cschi

!!! Nicht getestet!!!
"""

import subprocess
import time
from threading import Thread

output_dir = "/home/hell/sw/bmsCS/logging/"
ip1 = "192.168.0.10"
ip2 = "192.168.0.1"
ip3 = "127.0.0.1"

# Erstelle das Ausgabeverzeichnis, falls es nicht existiert
subprocess.run(["mkdir", "-p", output_dir])

def capture_traffic():
    # Aktuelles Datum und Stunde ermitteln
    current_date = time.strftime("%Y%m%d")
    current_hour = time.strftime("%H")

    pcap_file = f"{output_dir}/{current_date}-{current_hour}.pcap"
    subprocess.run(["sudo", "tcpdump", "-i", "lo", f"host {ip1} and host {ip2} or host {ip3}", "-w ", pcap_file])

def main():
    current_hour = time.strftime("%H")

    while True:
        if time.strftime("%H") != current_hour:
            current_hour = time.strftime("%H")
            
            # If the hour has changed, stop the previous thread
            if 'traffic_thread' in locals() and traffic_thread.is_alive():
                traffic_thread.join()
                
            # Start a new thread
            traffic_thread = Thread(target=capture_traffic)
            traffic_thread.start()

        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()

