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
        self.link = ""
        self.telescope = ""
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
    def SetLink(self,link):
        self.link = link

def log(message):
    fop = open("GA.log",'a')
    fop.write(str(message))
    fop.close()

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
	    GenHTML(ev.datestr,ev.RA,ev.DEC,nicedate,h,secz,ev.telescope)
	    if ev.link != "":
	      webbrowser.open_new_tab(ev.link)
	    webbrowser.open_new_tab(os.path.join(os.getcwd(),htmlfile))
        if not flag:        
            obj.SetAlert()
            gotUVOT = False
            while not gotUVOT:
	      # updating and parsing
	      # until not received UVOT position
	      data = GetData(obj,ev.link)
	      gotUVOT = self.ParseUVOT(data,obj)
	      time.sleep(10)
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
                     self.RiseAlert(obj,ev,flag)
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

def Update(obj):
    global url
    data = GetData(obj,url)
    SaveData(data)
    Handler(obj,data)

class TerminalViewer(QtGui.QWidget):
    def __init__(self,app,parent=None):
        desk = QtGui.QApplication.desktop() #remove hanging on Windows shutdown
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


class MainWindow(QtGui.QMainWindow):
        def __init__(self, tv, win_parent = None):
		#Init the base class
		self.tv = tv
		QtGui.QMainWindow.__init__(self, win_parent)
		self.create_widgets()
		traySignal = "activated(QSystemTrayIcon::ActivationReason)"
		QtCore.QObject.connect(self.tv.trayIcon, QtCore.SIGNAL(traySignal), self.__icon_activated)

	def create_widgets(self):
		#Widgets
                self.movie_screen = QtGui.QLabel()
	        self.movie_screen.setSizePolicy(QtGui.QSizePolicy.Expanding, 
                                                QtGui.QSizePolicy.Expanding)        
                self.movie_screen.setAlignment(QtCore.Qt.AlignCenter)
                self.movie = QtGui.QMovie("anim.gif", QtCore.QByteArray(), self) 
                self.movie.setCacheMode(QtGui.QMovie.CacheAll) 
                self.movie.setSpeed(100) 
                self.movie_screen.setMovie(self.movie) 
                self.movie.start()
		self.label = QtGui.QLabel("SWIFT GRB alert")
		self.label.setAlignment(QtCore.Qt.AlignCenter)
		self.last_button = QtGui.QPushButton("Show Last GRB")
		self.info_button = QtGui.QPushButton("Info")
		self.reset_button = QtGui.QPushButton("Reset")
		self.config_button = QtGui.QPushButton("Configure")
		self.quit_button = QtGui.QPushButton("Quit program")
		self.setWindowTitle("GRB Alert")
		#connect signals
		QtCore.QObject.connect(self.last_button,
		        QtCore.SIGNAL("clicked()"),
		        self.on_last_clicked)
		QtCore.QObject.connect(self.info_button,
			QtCore.SIGNAL("clicked()"),
			self.on_info_clicked)
		QtCore.QObject.connect(self.reset_button,
			QtCore.SIGNAL("clicked()"),
			self.on_reset_clicked)
		QtCore.QObject.connect(self.config_button,
			QtCore.SIGNAL("clicked()"),
			self.on_config_clicked)
		QtCore.QObject.connect(self.quit_button,
			QtCore.SIGNAL("clicked()"),
			QtGui.qApp,
			QtCore.SLOT('quit()'))


		#vert layout
		v_box = QtGui.QVBoxLayout()
		v_box.addWidget(self.movie_screen)
		v_box.addWidget(self.label)
		v_box.addWidget(self.last_button)
		v_box.addWidget(self.info_button)
		v_box.addWidget(self.reset_button)
		v_box.addWidget(self.config_button)
		v_box.addWidget(self.quit_button)
		#Create central widget, add layout and set
		central_widget = QtGui.QWidget()
		central_widget.setLayout(v_box)
		self.setCentralWidget(central_widget)

	def on_last_clicked(self):
		self.tv.ShowLast()
	def on_info_clicked(self):
		self.tv.ShowAbout()
	def on_reset_clicked(self):
		self.tv.UnsetAlert()
	def on_config_clicked(self):
		webbrowser.open("config.cfg")
	def okayToClose(self): return False
	def closeEvent(self, event):
		if self.okayToClose(): 
		  #user asked for exit
		  self.tv.trayIcon.hide()
		  event.accept()
		else:
		  #"minimize"
		  self.hide()
		  self.tv.trayIcon.show()
		  event.ignore()

	def __icon_activated(self, reason):
	        self.setGeometry(600, 400, 250, 150)
		if reason == QtGui.QSystemTrayIcon.DoubleClick:
		  self.show()
		if reason == QtGui.QSystemTrayIcon.Trigger:
		  self.show()
		if reason == QtGui.QSystemTrayIcon.MiddleClick:
		  self.show()

def main():
    app = QtGui.QApplication(sys.argv)
    qb = TerminalViewer(app)
    main_window = MainWindow(qb)
    sys.exit(app.exec_())



if __name__ == '__main__':
    main()
