#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 23:10:44 2011

@author: Dmitriy Blinov
"""
import sys,os
from PyQt4 import QtGui
from PyQt4.QtCore import SLOT
from PyQt4.QtCore import SIGNAL
from PyQt4 import QtCore
import time
import math
from urllib2 import urlopen
from urllib2 import URLError
import lxml.html
from StringIO import StringIO
from datetime import datetime
import sidereal
import webbrowser
from GenHTML import GenHTML
import ConfigParser

url = "http://skyalert.org/feeds/144"
htmlfile = "FindingChart.html"
aboutfile = "About.html"
timeout = 600


config = ConfigParser.RawConfigParser()
config.read('config.cfg')

longitude = config.getfloat('location', 'longitude')
latitude = config.getfloat('location', 'latitude')
altitude = config.getfloat('location', 'altitude')
alt_limit = config.getfloat('GRBparams', 'alt_limit')
timeout = config.getint('scanparams', 'timeout')
url = config.get('scanparams', 'swifturl')
htmlfile = config.get('info', 'htmlfile')
aboutfile = config.get('info', 'aboutfile')
usefermi = config.getboolean('scanparams', 'usefermi')

class Event():
    def __init__(self):
        self.datestr = ""
        self.date = 0
        self.RA = 0
        self.DEC = 0
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
    def GetDate(self):
        date = self.datestr.rstrip("Z").split(".")[0]
        return datetime.strptime(date,"%Y-%m-%dT%H:%M:%S")
    def GetFormDate(self):
        day = self.datestr.split("T")[0]
        timestr = self.datestr.split("T")[1].rstrip("Z")
        return day + " " + timestr

def log(message):
    fop = open("GA.log",'a')
    fop.write(str(message))
    fop.close()

def GetData(obj):
    try:
        f = urlopen(url)
        s = f.read()
        f.close()
    except URLError, e:
        log(e)
        obj.SetWarn()
        return ""
    else:
        return s

def GetData1(obj):
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
    def __init__(self,obj,data):
        self.Parse(obj,data)
    def CalcAlt(self,ev):
        curtime = datetime.now()
        Gst = sidereal.SiderealTime.fromDatetime(curtime)
        Lst = Gst.lst(math.radians(longitude))
        Lst = Lst.hours * 15 #local siderial time - in degrees
        hourangle = red_to_pos(Lst-ev.RA)
        RADec = sidereal.RADec(math.radians(ev.RA), math.radians(ev.DEC))
        AltAz = RADec.altAz(math.radians(hourangle*15.0), math.radians(latitude))
        return math.degrees(AltAz.alt)
    def RiseAlert(self,obj,ev,flag):
        #flag show whether it's called from GUI
        #ev.CalcDate()
        h = round(self.CalcAlt(ev),2)
        secz = round(1.0/math.cos(math.pi*0.5-math.radians(h)),2)
        
        if h > alt_limit or flag:
            nicedate = ev.GetFormDate()
	    GenHTML(ev.datestr,ev.RA,ev.DEC,nicedate,h,secz)        
	    webbrowser.open_new_tab(os.path.join(os.getcwd(),htmlfile))
        if not flag:        
            obj.SetAlert()
    def ShowLast(self,obj):
        ev = Handler.EventList[-1]
        for event in Handler.EventList:
            if event.GetDate() > ev.GetDate():
                ev = event
        flag = True #called from GUI
        self.RiseAlert(obj,ev,flag)
    def Parse(self,obj,data):
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
                 if (ev not in Handler.EventList) and Handler.FirstParsing:
                     Handler.EventList.append(ev)
                 elif ev not in Handler.EventList:
                     Handler.EventList.append(ev)
                     flag = False #called not from GUI
                     self.RiseAlert(obj,ev,flag)
        Handler.FirstParsing = False

def Update(obj):
    data = GetData(obj)
    SaveData(data)
    Handler(obj,data)

class TerminalViewer(QtGui.QWidget):
    def __init__(self,app,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.Label = QtGui.QLabel("Waiting for Something",self)
        self.trayIcon = QtGui.QSystemTrayIcon(QtGui.QIcon("green.png"), app)
        self.menu = QtGui.QMenu()
        self.lastAction = self.menu.addAction("Show Last")
        self.resetAction = self.menu.addAction("Reset")
        self.aboutAction = self.menu.addAction("About")        
        self.exitAction = self.menu.addAction("Exit")
        self.trayIcon.setContextMenu(self.menu)

        self.DataCollector = TerminalX(self)
        self.connect(self.DataCollector,QtCore.SIGNAL("Activated ( QString ) "), self.Activated)
        self.DataCollector.start()

        self.trayIcon.show()
        self.exitAction.connect(self.exitAction, SIGNAL("triggered()"), app, SLOT("quit()"))
        self.resetAction.connect(self.resetAction, SIGNAL("triggered()"), self.UnsetAlert)
        self.aboutAction.connect(self.aboutAction, SIGNAL("triggered()"), self.ShowAbout)
        self.lastAction.connect(self.lastAction, SIGNAL("triggered()"), self.ShowLast)
        self.UpdateData()
        self.connect(self.DataCollector,QtCore.SIGNAL("UpdateData() "), self.UpdateData)
    def Activated(self,newtext):
        self.Label.setText(newtext)
    def SetWarn(self):
        self.trayIcon.setIcon(QtGui.QIcon("yellow.png"))
    def SetAlert(self):
        self.trayIcon.setIcon(QtGui.QIcon("red.png"))
    def UnsetAlert(self):
        self.trayIcon.setIcon(QtGui.QIcon("green.png"))
    def UpdateData(self):
        Update(self)
    def ShowAbout(self):
        webbrowser.open_new_tab(os.path.join(os.getcwd(),aboutfile))
    def ShowLast(self):
        Handler(self," ").ShowLast(self)
    def closeEvent(self,e):
        e.accept()
        app.exit()

class TerminalX(QtCore.QThread):
    def __init__(self,parent=None):
        QtCore.QThread.__init__(self,parent)

    def run(self):
        global timeout
        while True:
            time.sleep(timeout)
            self.emit(QtCore.SIGNAL("UpdateData()"))
            print "################################################"


def main():
    app = QtGui.QApplication(sys.argv)
    qb = TerminalViewer(app)
    sys.exit(app.exec_())



if __name__ == '__main__':
    main()
