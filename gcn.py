#Class for handling GCN packets from both our router and new VOevent system
import lxml.html
from StringIO import StringIO
import event
import log
from datetime import datetime
import sidereal
import math
from GenHTML import GenHTML
import webbrowser
import os

def red_to_pos(hourang):
    #receives hourang in degrees
    #returns reduced to positive in hours
    if hourang < 0:
        hourang = 24 + hourang/15.0
    else:
        hourang = hourang/15.0
    return hourang

class GCNHandler():
    def __init__(self, obj, data, conf):
        self.conf = conf
        self.ev = event.Event()
        fop = open("latest_packet.xml",'w')
        #print data
        fop.write(data)
        fop.close()
        self.Parse(obj, data)
    def CalcAlt(self,ev):
        curtime = datetime.now()
        Gst = sidereal.SiderealTime.fromDatetime(curtime)
        Lst = Gst.lst(math.radians(self.conf.longitude))
        Lst = Lst.hours * 15 #local siderial time - in degrees
        hourangle = red_to_pos(Lst-ev.RA)
        RADec = sidereal.RADec(math.radians(ev.RA), math.radians(ev.DEC))
        AltAz = RADec.altAz(math.radians(hourangle*15.0), math.radians(self.conf.latitude))
        return math.degrees(AltAz.alt)
    def CheckCoordErr(self,ev):
        if ev.Cerr < self.conf.coorerr:
	  return True
	else:
	  return False
    def RiseAlert(self,obj,flag):
        #flag show whether it's called from GUI
        #ev.CalcDate()
        ev = self.ev
        h = round(self.CalcAlt(ev),2)
        secz = round(1.0/math.cos(math.pi*0.5-math.radians(h)),2)
        if not self.CheckCoordErr(ev):
	    log.log('Source position err is too big')
	    return 0
        if h > self.conf.alt_limit or flag:
            nicedate = ev.GetFormDate()
	    GenHTML(ev.datestr,ev.RA,ev.DEC,nicedate,h,secz,ev.telescope,ev.Cerr)
	    if ev.link != "":
	      webbrowser.open_new_tab(ev.link)
	    webbrowser.open_new_tab(os.path.join(os.getcwd(),self.conf.htmlfile))
        if not flag:        
            obj.SetAlert()
    def Parse(self,obj,data):
      isVOEvent = False
      pars = lxml.html.etree.HTMLParser()
      tree = lxml.html.etree.parse(StringIO(data),pars)
      for parent in tree.getiterator():
        if parent.tag == "voevent":
	  isVOEvent = True
          ev = event.Event()
      if not isVOEvent:
	log.log('Caught not VO event')
	return 0
      for parent in tree.getiterator():
	if parent.tag == "what":
          for i in range(len(parent)):
            if parent[i].tag == "param":
	      if parent[i].attrib.get("name") == 'Packet_Type':
		ev.SetType(parent[i].attrib.get("value"))
		log.log('Caught event type '+str(ev.etype))
		if not ev.IsInteresting():
		  print "Not interesting event"
		  return 0
      for parent in tree.getiterator():
	if parent.tag == "position2d":
	  for i in range(len(parent)):
	    if parent[i].tag == "value2":
	      ev.SetRA(parent[i][0].text)
	      ev.SetDEC(parent[i][1].text)
	    elif parent[i].tag == "error2radius":
	      ev.SetCerr(parent[i].text)
      for parent in tree.getiterator():
	if parent.tag == "timeinstant":
	  for i in range(len(parent)):
	    if parent[i].tag == "isotime":
	      ev.datestr = parent[i].text
	      self.ev = ev
      fop = open("latest_grb_packet.xml",'w')
      fop.write(data)
      fop.close()
      self.RiseAlert(obj,True)
 
