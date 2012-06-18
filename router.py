#Functions for handling connvections to out router of old GCN system
import config
import socket
import log
import gcn
import sys

sockettimeout = 60 #reconnects every N sec

def recv_end(the_socket,conf):
    data=''
    while True:
            try:
	      data=the_socket.recv(conf.datalength)
	    except socket.error, msg:
	      log.log('Could not open socket '+str(msg))
	      return False
            return data

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
	data = recv_end(s,conf) #s.recv(conf.datalength)
	if data:
	  gcn.GCNHandler(obj,data,conf)
	else:# if GCN is disconnected from our router
	  log.log('Disconnected from socket')
	  break

