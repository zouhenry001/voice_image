#Encoding=UTF-8

import logging

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
# logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG, filename='/data/vophoto/src/app.log')

def debug(msg):
    logging.debug(msg)

def info(msg):
    logging.info(msg)
    
def error(msg):
    logging.error(msg)

