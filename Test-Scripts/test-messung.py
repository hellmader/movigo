#!/usr/bin/python3

import logging
from clLogger import CsvFormatter,CsvRotatingFileHandler,RotatingCsvLogger
import time

DELIMITER=';'
DL=DELIMITER
LOG_FILE_NAME = '/home/hell/log/messwert.csv'
LOG_MAX_SIZE = 500000 # Max size of each log file in bytes
LOG_MAX_FILES = 20 # Max of files count
LOG_HEADER = 'Datum;Zeit;Spannung;Strom'
LOG_FORMAT = '%(asctime)s'+DELIMITER+'%(message)s' # Log record format can use: asctime, levelname
LOG_DATE_FORMAT = '%d.%m.%Y'+DELIMITER+'%H:%M:%S'


print("messung laeuft...")


def main():
    # Creat logger with csv rotating handler
    logger = RotatingCsvLogger(logging.INFO, LOG_FORMAT, LOG_DATE_FORMAT,
        LOG_FILE_NAME, LOG_MAX_SIZE, LOG_MAX_FILES, LOG_HEADER)

    # Log some records
    while True:

      # You can log list or string
      logger.info('24,50'+DL+'28,20')
      time.sleep(.1)

      # Note that "LOG_HEADER" will only appear in the rotated files (that ends with _1 _2..) 

if __name__ == '__main__':
    main()
