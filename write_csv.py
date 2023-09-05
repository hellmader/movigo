#!/usr/bin/python

########################################################################
# V1.0
########################################################################

import time
import threading
import enum
import logging
from clHelper import checkTime
import pandas as pd
import time, sys
from datetime import datetime
import csv
import os
import queue
from collections import deque

class Request(enum.Enum):
    NONE = 0
    BASIC_INFO = 1
    CELL_VOLTAGE = 2

def current_milli_time():
    return round(time.time() * 1000)

class write_csv (threading.Thread):
    def __init__(self, debugOutput, updateCycle, write_to_csv):
        threading.Thread.__init__(self)
        self.debugOutput = debugOutput
        self.updateCycle = updateCycle
        self.write_to_csv = write_to_csv
        self.running = True
        self.max_file_size = 10 * 1024 *2 *1000  # 10 MB
        self.max_files = 100  # 10MB*100 files => 1GB max in directory /home/hell/sw/bms/logging/csv/
        self.current_file_index = self.get_newest_file_index() + 1
        self.files_queue = deque()  # Initialize an empty queue
        self.fill_files_queue()  # Fill up the queue with existing indices
        self.create_new_file()

        
    
    def fill_files_queue(self):
        existing_indices = set()
        for filename in os.listdir('/home/hell/sw/bms/logging/csv/'):
            if filename.startswith('data') and filename.endswith('.csv'):
                try:
                    index = int(filename[4:-4])  # Extract the index from the filename
                    existing_indices.add(index)
                except ValueError:
                    pass  # Ignore filenames that don't match the expected format
        for index in existing_indices:
            self.files_queue.append(index)

    
    def get_newest_file_index(self):
        existing_indices = set()
        for filename in os.listdir('/home/hell/sw/bms/logging/csv/'):
            if filename.startswith('data') and filename.endswith('.csv'):
                try:
                    index = int(filename[4:-4])  # Extract the index from the filename
                    existing_indices.add(index)
                except ValueError:
                    pass  # Ignore filenames that don't match the expected format
        if existing_indices:
            return max(existing_indices)
        return 0



    def create_new_file(self):
          num_existing_files = sum(1 for filename in os.listdir('/home/hell/sw/bms/logging/csv/') if filename.startswith('data') and filename.endswith('.csv'))
          
          while num_existing_files >= self.max_files:
              oldest_index = self.files_queue.popleft()
              self.delete_oldest_file(oldest_index)
              num_existing_files -= 1
              
          while self.current_file_index in self.files_queue:
              self.current_file_index += 1
              if self.current_file_index > self.max_files:
                  self.current_file_index = 1
              
          self.file_size = 0
          self.current_file = open(f'/home/hell/sw/bms/logging/csv/data{self.current_file_index}.csv', 'w', newline='')
          self.files_queue.append(self.current_file_index)
      
          
    def delete_oldest_file(self, index):
        oldest_filename = f'/home/hell/sw/bms/logging/csv/data{index}.csv'
        if os.path.exists(oldest_filename):
            os.remove(oldest_filename)

    

    


    def write(self, data):
        if self.file_size + self.current_file.tell() >= self.max_file_size:
            self.current_file.close()
            self.current_file_index += 1
            self.create_new_file()


        writer = csv.DictWriter(self.current_file, fieldnames=data.keys(), delimiter=';')
        if self.file_size == 0:
            writer.writeheader()
        writer.writerow(data)
        self.file_size = self.current_file.tell()

    def stop(self):
        self.running = False

    def run(self):
        if self.debugOutput:
            print("can: Run - Start Thread")

        while self.running:
            try:
                qDataIn = self.write_to_csv.get(timeout=1)
                self.write(qDataIn)
            except queue.Empty:
                pass

        if self.current_file:
            self.current_file.close()

        if self.debugOutput:
            print("canO: Thread exit")

# Create and start the thread
# debugOutput = True
# updateCycle = 100
# write_to_csv = ...
# thread = write_csv(debugOutput, updateCycle, write_to_csv)
# thread.start()
