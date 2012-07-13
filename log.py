#obviously logging functions
import time
import os
#import logging
#import logging.handlers



#def log1(message):
  #LOG_FILENAME = 'GA.log'

  #logger = logging.getLogger('Logger')
  ##logging.basicConfig(format='%(asctime)s %(message)s')
  #logger.setLevel(logging.INFO)

  #handler = logging.handlers.RotatingFileHandler(
              #LOG_FILENAME, maxBytes=1000000, backupCount=5)

  #logger.addHandler(handler)
  #logger.info(message)


def log(message):
  fop = open("GA.log",'a')
  fop.write(time.strftime("%d.%m %H:%M:%S ")+str(message)+"\n")
  fop.close()

def init():
  fop = open("GA.log",'a')
  fop.close()
  statinfo = os.stat("GA.log")
  if statinfo.st_size > 1e6:
    fop = open("GA.log",'w')
    fop.write("New log started on "+time.strftime("%d.%m %H:%M:%S ")+"\n")
    fop.close()