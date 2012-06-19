#obviously logging functions
import time

def log(message):
    fop = open("GA.log",'a')
    fop.write(time.strftime("%d.%m %H:%M:%S ")+str(message)+"\n")
    fop.close()

