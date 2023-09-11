import subprocess
import time
import os
from collections import deque

def start_tcpdump_subprocess(interface, output_filename):
    with open(output_filename, "a") as output_file:
        command = ['sudo','tcpdump', '-i', interface, '-w', output_filename]
        process = subprocess.Popen(command, stdout=output_file, stderr=subprocess.STDOUT)
        return process

def main():
    log_directory = "/home/hell/sw/bms/logging"
    max_log_size = 1024 * 10000  # 10 MB
    max_files = 100 #10MB*100 files => 1GB max each in directory /home/hell/sw/bms/logging/lo and /home/hell/sw/bms/logging/eth0 

    # TCP capture on eth0
    eth0_log_directory = os.path.join(log_directory, "tcp", "eth0")
    eth0_log_index = get_newest_log_index(eth0_log_directory) + 1
    eth0_output_filename = os.path.join(eth0_log_directory, f"eth0_capture_{eth0_log_index}.pcap")
    eth0_files_queue = deque()

    #print("Starting initial tcpdump subprocess for eth0. Output will be saved to", eth0_output_filename)
    eth0_tcpdump_process = start_tcpdump_subprocess("eth0", eth0_output_filename)

    # TCP capture on lo with host 127.0.0.1
    lo_log_directory = os.path.join(log_directory, "tcp", "lo")
    lo_log_index = get_newest_log_index(lo_log_directory) + 1
    lo_output_filename = os.path.join(lo_log_directory, f"lo_capture_{lo_log_index}.pcap")
    lo_files_queue = deque()

    #print("Starting initial tcpdump subprocess for lo. Output will be saved to", lo_output_filename)
    lo_tcpdump_process = start_tcpdump_subprocess("lo", lo_output_filename)

    # Initialize eth0 files queue with existing indices
    for filename in os.listdir(eth0_log_directory):
        if filename.startswith('eth0_capture_') and filename.endswith('.pcap'):
            try:
                index = int(filename[len('eth0_capture_'):-len('.pcap')])
                eth0_files_queue.append(index)
            except ValueError:
                pass

    # Initialize lo files queue with existing indices
    for filename in os.listdir(lo_log_directory):
        if filename.startswith('lo_capture_') and filename.endswith('.pcap'):
            try:
                index = int(filename[len('lo_capture_'):-len('.pcap')])
                lo_files_queue.append(index)
            except ValueError:
                pass

    try:
        while True:
            time.sleep(2)  # Check every 2 seconds

            eth0_file_size = os.path.getsize(eth0_output_filename)
            #print("Current eth0 file size:", eth0_file_size)

            if eth0_file_size > max_log_size:
                #print("Stopping current eth0 tcpdump subprocess.")
                eth0_tcpdump_process.terminate()
                eth0_tcpdump_process.wait()

                while len(eth0_files_queue) >= max_files:
                    oldest_index = eth0_files_queue.popleft()
                    delete_oldest_file(eth0_log_directory, f"eth0_capture_{oldest_index}.pcap")

                eth0_log_index += 1
                eth0_output_filename = os.path.join(eth0_log_directory, f"eth0_capture_{eth0_log_index}.pcap")
                eth0_files_queue.append(eth0_log_index)

                #print("Starting new eth0 tcpdump subprocess. Output will be saved to", eth0_output_filename)
                eth0_tcpdump_process = start_tcpdump_subprocess("eth0", eth0_output_filename)

            lo_file_size = os.path.getsize(lo_output_filename)
            #print("Current lo file size:", lo_file_size)

            if lo_file_size > max_log_size:
                #print("Stopping current lo tcpdump subprocess.")
                lo_tcpdump_process.terminate()
                lo_tcpdump_process.wait()

                while len(lo_files_queue) >= max_files:
                    oldest_index = lo_files_queue.popleft()
                    delete_oldest_file(lo_log_directory, f"lo_capture_{oldest_index}.pcap")

                lo_log_index += 1
                lo_output_filename = os.path.join(lo_log_directory, f"lo_capture_{lo_log_index}.pcap")
                lo_files_queue.append(lo_log_index)

                #print("Starting new lo tcpdump subprocess. Output will be saved to", lo_output_filename)
                lo_tcpdump_process = start_tcpdump_subprocess("lo", lo_output_filename)

    except KeyboardInterrupt:
        print("\nStopping the script.")

def get_newest_log_index(directory):
    existing_indices = set()
    for filename in os.listdir(directory):
        if filename.startswith('eth0_capture_') and filename.endswith('.pcap'):
            try:
                index = int(filename[len('eth0_capture_'):-len('.pcap')])
                existing_indices.add(index)
            except ValueError:
                pass
        if filename.startswith('lo_capture_') and filename.endswith('.pcap'):
            try:
                index = int(filename[len('lo_capture_'):-len('.pcap')])
                existing_indices.add(index)
            except ValueError:
                pass
    if existing_indices:
        return max(existing_indices)
    return 0

def delete_oldest_file(directory, filename):
    oldest_filename = os.path.join(directory, filename)
    if os.path.exists(oldest_filename):
        os.remove(oldest_filename)

if __name__ == "__main__":
    main()
