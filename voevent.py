#Handling connections to VOEvent servers
import config
import socket
import itertools
import struct
import log
import gcn
import lxml.html
import time
from lxml import etree
from StringIO import StringIO
import threading

pktlen = 2048
maxpktlen = 30000
imaldiff = 200 #if doesn't receive iamalive in this time diff (sec) then reconnect

def makeResp(xml):
  tree = etree.fromstring(xml) 
  elems = tree.xpath("//TimeStamp") 

  bingoCounter = 0  
  elem = elems[0]
  parent = elem.getparent() 
  subIter = parent.iter() 
  newElem = etree.Element("Meta")
  newElem.tail = "\n" 
  #newElem.append( etree.Element('Param') )
  atr = {"name":"IPAddr","value":"195.19.250.180"}
  etree.SubElement(newElem,'Param', atr)
  atr = {"name":"Contact","value":"dmitriy.blinov@gmail.com"}
  etree.SubElement(newElem,'Param', atr)
  etree.SubElement(newElem,'Result').text = "Message received and validated successfully"
  parent.insert(3, newElem) 
        
  newXml = etree.tostring(tree)
  resp = newXml
  print newXml
  return resp

def respIfImAlive(xml):
  isImAlive = False
  pars = lxml.html.etree.HTMLParser()
  tree = lxml.html.etree.parse(StringIO(xml),pars)
  for parent in tree.getiterator():
    if parent.tag == "transport":
      isImAlive = True
      log.log('Caught Transport packet')
  return isImAlive

def GUI_thread(obj,xml,conf):
  gcn.GCNHandler(obj,xml,conf)
  return

def voserver_thread(obj):
  conf = config.Config()
  lastiamalive = time.time()
  socketipiter = itertools.cycle(conf.voeventips) #infinite iterator through the list
  socketport = conf.voeventport
  while True:
    socketip = socketipiter.next()
    for sockatr in socket.getaddrinfo(socketip, socketport, socket.AF_INET, socket.SOCK_STREAM):
      af, socktype, proto, canonname, sa = sockatr
      try:
	s = socket.socket(af, socktype, proto)
	s.settimeout(imaldiff)
      except socket.error, msg:
	continue
      try:
	s.connect(sa)
      except socket.error, msg:
	s = None
	continue
    if s is None:
      continue
    log.log('Connected to '+ socketip)
    while True:
      if (time.time() - lastiamalive) > imaldiff+2:
	lastiamalive = time.time()
	#try to connect to another server
	break
      try:
        data = s.recv(4)
      except:
	pass
      dl = struct.unpack('>I', data)[0] #big-endian 4 byte int
      if dl > 30000:
	log.log("Too much data received = " + str(dl))
	break
      read = 0
      xml = ""
      while read < dl:
	remains = dl-read
	if remains < pktlen:
	  try:
	    xml = xml + s.recv(remains)
	    read = len(xml)
	  except:
	    pass
	else:
	  try:
            xml = xml + s.recv(pktlen)
            read = len(xml)
          except:
	    pass
      if respIfImAlive(xml):
	lastiamalive = time.time()
	respmsg = makeResp(xml)
	resplen = struct.pack('>I',len(respmsg))
	s.send(resplen)
	s.send(respmsg)
      else:
	#separate thread to prevent gui locks
	GUIalert = threading.Thread(name='GUIalert', target=GUI_thread, args=(obj,xml,conf))
	GUIalert.start()
  return
