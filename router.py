#Functions for handling connvections to out router of old GCN system
import config
import socket
import log
import gcn
import sys
import time

sockettimeout = 120 #waiting for data this time
timoutifnoconn = 5 #if couldnt establish connection with socket will sleep for this timeout

def gcn_thread(obj,StopThreadFlag):
    conf = config.Config()
    while True:
      for res in socket.getaddrinfo(conf.socketip, conf.socketport, socket.AF_INET, socket.SOCK_STREAM):
	af, socktype, proto, canonname, sa = res
	try:
	  s = socket.socket(af, socktype, proto)
	  s.settimeout(sockettimeout)
	except socket.error, msg:
	  log.log('Could not open socket '+str(msg))
	  s = None
	  continue
	try:
	  time.sleep(timoutifnoconn)
	  s.connect(sa)
	  log.log('Connected to socket ')
	except socket.error, msg:
	  log.log('Could not open socket '+str(msg))
	  s.close()
	  s = None
	  time.sleep(1)
	  continue
	break
      if s is None:
	log.log('Could not open socket')
	continue
      while True:
	if StopThreadFlag[0]:
	  log.log('Program closed')
	  sys.exit(0)
	try:
	  data = s.recv(conf.datalength) #recv_end(s,conf)
	except:
	  log.log('Timeout on router socket')
	  break
	if data:
	  gcn.GCNHandler(obj,data,conf)
	else:# if GCN is disconnected from our router
	  log.log('Disconnected from socket')
	  break

