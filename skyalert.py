from urllib2 import urlopen
from urllib2 import URLError
import lxml.html
from StringIO import StringIO
from datetime import datetime
import sidereal
import webbrowser
import math
from GenHTML import GenHTML
import os

def log(message):
    fop = open("GA.log",'a')
    fop.write(str(message)+"\n")
    fop.close()

class Event():
    def __init__(self):
        self.datestr = ""
        self.date = 0
        self.RA = 0
        self.DEC = 0
        self.Cerr = 0
        self.link = ""
        self.telescope = ""
        self.etype = 0 #3   : "Imalive",
        self.types = { 53  : "INTEGRAL_WAKEUP",
                       54  : "INTEGRAL_REFINED",
                       55  : "INTEGRAL_OFFLINE",
                       61  : "SWIFT_BAT_GRB_POS",
                       67  : "SWIFT_XRT_POS",
                       81  : "SWIFT_UVOT_POS",
                       101 : "SuperAGILE_GRB_POS_GROUND",
                       102 : "SuperAGILE_GRB_POS_REFINED",
                       112 : "FERMI_GBM_GND_POS",
                       134 : "MAXI_UNKNOWN_SOURCE"
                     }
    def __ne__(self,other):
        return self.datestr.__ne__(other.datestr)
    def __eq__(self,other):
        return self.datestr.__eq__(other.datestr)
    def CalcDate(self):
        pass #self.datestr
    def SetRA(self,RA):
        self.RA = float(RA)
    def SetDEC(self,DEC):
        self.DEC = float(DEC)
    def SetCerr(self,Cerr):
        self.Cerr = float(Cerr)
    def SetType(self,typ):
        self.etype = int(typ)
        if self.types.has_key(self.etype):
	  self.telescope = self.types[self.etype]
	else:
	  self.telescope = "Not interesting"
    def IsInteresting(self):
        return self.types.has_key(self.etype)
    def GetDate(self):
        date = self.datestr.rstrip("Z").split(".")[0]
        return datetime.strptime(date,"%Y-%m-%dT%H:%M:%S")
    def GetFormDate(self):
        day = self.datestr.split("T")[0]
        timestr = self.datestr.split("T")[1].rstrip("Z")
        return day + " " + timestr
    def SetLink(self,link):
        self.link = link

def GetData(obj,url):
    try:
        f = urlopen(url)
        s = f.read()
        f.close()
    except URLError, e:
        log(e)
        obj.SetWarn()
        return " "
    else:
        return s

def GetData1(obj,url):
    fop = open("ex.xml",'r')
    s = fop.read()
    fop.close()
    return s

def SaveData(data):
    fop = open("latest_data.xml",'w')
    fop.write(data)
    fop.close()

def red_to_pos(hourang):
    #receives hourang in degrees
    #returns reduced to positive in hours
    if hourang < 0:
        hourang = 24 + hourang/15.0
    else:
        hourang = hourang/15.0
    return hourang

class Handler():
    FirstParsing = True
    EventList = []
    def __init__(self,obj,data,conf):
        self.Parse(obj,data,conf)
    def CalcAlt(self,ev,conf):
        curtime = datetime.now()
        Gst = sidereal.SiderealTime.fromDatetime(curtime)
        Lst = Gst.lst(math.radians(conf.longitude))
        Lst = Lst.hours * 15 #local siderial time - in degrees
        hourangle = red_to_pos(Lst-ev.RA)
        RADec = sidereal.RADec(math.radians(ev.RA), math.radians(ev.DEC))
        AltAz = RADec.altAz(math.radians(hourangle*15.0), math.radians(conf.latitude))
        return math.degrees(AltAz.alt)
    def RiseAlert(self,obj,ev,flag,conf):
        #flag show whether it's called from GUI
        #ev.CalcDate()
        h = round(self.CalcAlt(ev,conf),2)
        secz = round(1.0/math.cos(math.pi*0.5-math.radians(h)),2)
        
        if h > conf.alt_limit or flag:
            nicedate = ev.GetFormDate()
	    GenHTML(ev.datestr,ev.RA,ev.DEC,nicedate,h,secz,ev.telescope,None)
	    if ev.link != "":
	      webbrowser.open_new_tab(ev.link)
	    webbrowser.open_new_tab(os.path.join(os.getcwd(),conf.htmlfile))
        if not flag:        
            obj.SetAlert()
            gotUVOT = False
            while not gotUVOT:
	      # updating and parsing
	      # until not received UVOT position
	      data = GetData(obj,ev.link)
	      gotUVOT = self.ParseUVOT(data,obj)
	      time.sleep(10)
    def ShowLast(self,obj,conf):
        ev = Handler.EventList[-1]
        for event in Handler.EventList:
            if event.GetDate() > ev.GetDate():
                ev = event
        flag = True #called from GUI
        self.RiseAlert(obj,ev,flag,conf)
    def Parse(self,obj,data,conf):
        pars = lxml.html.etree.HTMLParser()
        tree = lxml.html.etree.parse(StringIO(data),pars)
        for parent in tree.getiterator():
             if parent.tag == "entry":
                 ev = Event()
                 for i in range(len(parent)):
                     if parent[i].tag == "published":
                         ev.datestr = parent[i].text
                     if parent[i].tag == "ra":
                         ev.SetRA(parent[i].text)
                     if parent[i].tag == "dec":
                         ev.SetDEC(parent[i].text)
                         ev.telescope = "BAT position"
                     if parent[i].tag == "link":
		         if parent[i].attrib["rel"] == "alternate":
			   # link to page with all info about the event
			   ev.SetLink(parent[i].attrib["href"])
                 if (ev not in Handler.EventList) and Handler.FirstParsing:
                     Handler.EventList.append(ev)
                 elif ev not in Handler.EventList:
                     Handler.EventList.append(ev)
                     flag = False #called not from GUI
                     self.RiseAlert(obj,ev,flag,conf)
        Handler.FirstParsing = False
    def ParseUVOT(self,data, obj):
        gotUVOT = False
        repl_data = data.replace("&lt;","<")
        data = repl_data.replace("&gt;",">")
        pars = lxml.html.etree.HTMLParser()
        tree = lxml.html.etree.parse(StringIO(data),pars)
        for parent in tree.getiterator():
	  if parent.tag == "voevent":
	    if "UVOT_Pos_" in parent.attrib["ivorn"]:
	      data = lxml.html.etree.tostring(parent[2], pretty_print=True)
	      gotUVOT = True
        repl_data = data.replace("\\r\\n', '    ","")
        pars = lxml.html.etree.HTMLParser()
        tree = lxml.html.etree.parse(StringIO(repl_data),pars)
        ev = Event()
        for parent in tree.getiterator():
	  if parent.tag == "isotime":
	    ev.datestr = parent.text.strip()
	  if parent.tag == "c1":
	    ev.SetRA(parent.text.strip())
	  if parent.tag == "c2":
	    ev.SetDEC(parent.text.strip())
	    ev.telescope = "UVOT position"
	if gotUVOT:
	  self.RiseAlert(obj,ev, True)
	  return gotUVOT
	else:
	  return gotUVOT

def Update(obj,conf):
    data = GetData(obj,conf.url)
    SaveData(data)
    Handler(obj,data,conf)
