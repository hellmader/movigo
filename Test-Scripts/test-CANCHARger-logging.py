#!/usr/bin/python

########################################################################
# V1.0
########################################################################


import os
import can
import time

import logging
from clLogger import CsvFormatter,CsvRotatingFileHandler,RotatingCsvLogger

DELIMITER=';'
DL=DELIMITER
LOG_FILE_NAME = '/home/hell/log/can-charger.csv'
LOG_MAX_SIZE = 500000 # Max size of each log file in bytes
LOG_MAX_FILES = 20 # Max of files count
LOG_HEADER = 'Datum;Zeit;Spannung;Strom'
LOG_FORMAT = '%(asctime)s'+DELIMITER+'%(message)s' # Log record format can use: asctime, levelname
LOG_DATE_FORMAT = '%d.%m.%Y'+DELIMITER+'%H:%M:%S'

logger = RotatingCsvLogger(logging.INFO, LOG_FORMAT, LOG_DATE_FORMAT,
        LOG_FILE_NAME, LOG_MAX_SIZE, LOG_MAX_FILES, LOG_HEADER)


CAN_filter = [{"can_id": 0x18FF50E5 , "can_mask": 0x1FFFFFFF, "extended": True}]
can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan', bitrate=500000, can_filters = CAN_filter)

timer = 0
    
while 1:
  time.sleep(.1)  #cpu friendly  
  msg = can0.recv(.2)
  logger.info(msg)
        
