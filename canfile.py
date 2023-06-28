import subprocess
import time
from threading import Thread

output_dir = "/home/hell/sw/bms/logging/can"

# Erstelle das Ausgabeverzeichnis, falls es nicht existiert
subprocess.run(["mkdir", "-p", output_dir])

def capture_can_traffic():
    # Aktuelles Datum und Stunde ermitteln
    current_date = time.strftime("%Y%m%d")
    current_hour = time.strftime("%H")

    log_file = f"{output_dir}/{current_date}-{current_hour}.log"
    with open(log_file, 'w') as outfile:
        subprocess.run(["sudo", "candump", "can0"], stdout=outfile)


def main():
    current_hour = time.strftime("%H")

    can_traffic_thread = Thread(target=capture_can_traffic)
    can_traffic_thread.start()
    while True:
        if time.strftime("%H") != current_hour:
            current_hour = time.strftime("%H")
            
            # If the hour has changed, stop the previous thread
            if 'can_traffic_thread' in locals() and can_traffic_thread.is_alive():
                can_traffic_thread.join()
                
            # Start a new thread
            can_traffic_thread = Thread(target=capture_can_traffic)
            can_traffic_thread.start()

        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
