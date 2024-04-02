import subprocess
import time
import os
from collections import deque

def start_candump_subprocess(output_filename):
    with open(output_filename, "a") as output_file:
        command = ['candump', 'can0']
        process = subprocess.Popen(command, stdout=output_file, stderr=subprocess.STDOUT)
        return process

def main():
    log_directory = "/home/hell/sw/bms/logging/can/"
    max_log_size = 1024 * 10000  # 10MB
    max_files = 100 #10MB*100 Files => 1GB max in directory /home/hell/sw/bms/logging/can
    log_index = get_newest_log_index(log_directory) + 1
    output_filename = os.path.join(log_directory, f"can{log_index}.log")
    files_queue = deque()

    #print("Starting initial candump subprocess. Output will be saved to", output_filename)
    candump_process = start_candump_subprocess(output_filename)

    # Initialize files queue with existing indices
    for filename in os.listdir(log_directory):
        if filename.startswith('can') and filename.endswith('.log'):
            try:
                index = int(filename[3:-4])
                files_queue.append(index)
            except ValueError:
                pass

    try:
        while True:
            time.sleep(2)  # Check every 2 seconds

            file_size = os.path.getsize(output_filename)
            #print("Current file size:", file_size)

            if file_size > max_log_size:
                print("Stopping current candump subprocess.")
                candump_process.terminate()
                candump_process.wait()

                while len(files_queue) >= max_files:
                    oldest_index = files_queue.popleft()
                    delete_oldest_file(log_directory, oldest_index)

                log_index += 1
                output_filename = os.path.join(log_directory, f"can{log_index}.log")
                files_queue.append(log_index)

                #print("Starting new candump subprocess. Output will be saved to", output_filename)
                candump_process = start_candump_subprocess(output_filename)

    except KeyboardInterrupt:
        print("\nStopping the script.")

def get_newest_log_index(directory):
    existing_indices = set()
    for filename in os.listdir(directory):
        if filename.startswith('can') and filename.endswith('.log'):
            try:
                index = int(filename[3:-4])
                existing_indices.add(index)
            except ValueError:
                pass
    if existing_indices:
        return max(existing_indices)
    return 0

def delete_oldest_file(directory, index):
    oldest_filename = os.path.join(directory, f"can{index}.log")
    if os.path.exists(oldest_filename):
        os.remove(oldest_filename)

if __name__ == "__main__":
    main()
