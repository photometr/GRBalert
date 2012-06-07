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
import lxml.html
from datetime import datetime
import sidereal
import webbrowser
from GenHTML import GenHTML
import ConfigParser
import threading
import socket
from skyalert import *


class Config():
    def __init__(self):
      config = ConfigParser.RawConfigParser()
      config.read('config.cfg')

      self.longitude = config.getfloat('location', 'longitude')
      self.latitude = config.getfloat('location', 'latitude')
      self.altitude = config.getfloat('location', 'altitude')
      self.coorerr = config.getfloat('location', 'coorerr')
      self.alt_limit = config.getfloat('GRBparams', 'alt_limit')
      self.timeout = config.getint('scanparams', 'timeout')
      self.url = config.get('scanparams', 'swifturl')
      self.htmlfile = config.get('info', 'htmlfile')
      self.aboutfile = config.get('info', 'aboutfile')
      self.usefermi = config.getboolean('scanparams', 'usefermi')
      self.socketip = config.get('scanparams', 'socketip')
      self.socketport = config.getint('scanparams', 'socketport')
      self.datalength = config.getint('scanparams', 'datalength')
      
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
                       82  : "SWIFT_BAT_GRB_POS_TEST",##############################
                       101 : "SuperAGILE_GRB_POS_GROUND",
                       102 : "SuperAGILE_GRB_POS_REFINED",
                       109 : "AGILE_GRB_POS_TEST",##################################
                       112 : "FERMI_GBM_GND_POS",
                       119 : "FERMI_GBM_GRB_POS_TEST",#############################
                       124 : "FERMI_LAT_GRB_POS_TEST",##############################
                       134 : "MAXI_UNKNOWN_SOURCE",
                       136 : "MAXI_TEST"#######################################
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

def log(message):
    fop = open("GA.log",'a')
    fop.write(str(message)+"\n")
    fop.close()


class GCNHandler():
    def __init__(self, obj, data, conf):
        self.conf = conf
        fop = open("latest_packet.xml",'w')
        print data
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
    def RiseAlert(self,obj,ev,flag):
        #flag show whether it's called from GUI
        #ev.CalcDate()
        h = round(self.CalcAlt(ev),2)
        secz = round(1.0/math.cos(math.pi*0.5-math.radians(h)),2)
        if not self.CheckCoordErr(ev):
	    log(time.strftime("%d.%m %H:%M:%S")+' source position err is too big')
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
          ev = Event()
      if not isVOEvent:
	log(time.strftime("%d.%m %H:%M:%S")+' Caught not VO event')
	return 0
      for parent in tree.getiterator():
	if parent.tag == "what":
          for i in range(len(parent)):
            if parent[i].tag == "param":
	      if parent[i].attrib.get("name") == 'Packet_Type':
		ev.SetType(parent[i].attrib.get("value"))
		log(time.strftime("%d.%m %H:%M:%S")+' Caught event type '+str(ev.etype))
		if not ev.IsInteresting():
		  print "Bad"
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
      self.RiseAlert(obj,ev,False)

def recv_end(the_socket,conf):
    End = "9Qhx5oxG0"
    total_data=[];data=''
    while True:
            try:
	      data=the_socket.recv(conf.datalength)
	    except socket.error, msg:
	      log(time.strftime("%d.%m %H:%M:%S")+' Could not open socket '+str(msg))
	      return False
            if data.endswith(End):
                total_data.append(data[:data.find(End)])
                break
            total_data.append(data)
            if len(total_data) > conf.datalength:
	        return ''.join(total_data) #to prevent memory leak
            if len(total_data)>1:
                #check if end_of_data was split
                last_pair=total_data[-2]+total_data[-1]
                if End in last_pair:
                    total_data[-2]=last_pair[:last_pair.find(End)]
                    total_data.pop()
                    break
    return ''.join(total_data)

def gcn_thread(obj):
    global socketip, socketport
    conf = Config()
    while True:
      for res in socket.getaddrinfo(conf.socketip, conf.socketport, socket.AF_INET, socket.SOCK_STREAM):
	af, socktype, proto, canonname, sa = res
	try:
	  s = socket.socket(af, socktype, proto)
	except socket.error, msg:
	  log(time.strftime("%d.%m %H:%M:%S")+' Could not open socket '+str(msg))
	  s = None
	  continue
	try:
	  s.connect(sa)
	  log(time.strftime("%d.%m %H:%M:%S")+' Connected to socket ')
	except socket.error, msg:
	  log(time.strftime("%d.%m %H:%M:%S")+' Could not open socket '+str(msg))
	  s.close()
	  s = None
	  Update(obj,conf) #will use the old source of data
	  time.sleep(conf.timeout)
	  continue
	break
      if s is None:
	log(time.strftime("%d.%m %H:%M:%S")+' Could not open socket')
	continue
      while True:
	data = recv_end(s,conf) #s.recv(conf.datalength)
	if data:
	  print data
	  GCNHandler(obj,data,conf)
	else:# if GCN is disconnected from our router
	  log(time.strftime("%d.%m %H:%M:%S")+' Disconnected from socket')
	  Update(obj,conf) #will use the old source of data
	  time.sleep(conf.timeout)
	  break

class TerminalViewer(QtGui.QWidget):
    def __init__(self,app,parent=None):
        self.conf = Config()
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
        self.connect(self.DataCollector,QtCore.SIGNAL("UpdateData() "), self.UpdateData)
        gcnthread = threading.Thread(name='gcn', target=gcn_thread, args=(self,))
        gcnthread.start()
    def Activated(self,newtext):
        self.Label.setText(newtext)
    def SetWarn(self):
        self.trayIcon.setIcon(QtGui.QIcon("yellow.png"))
    def SetAlert(self):
        self.trayIcon.setIcon(QtGui.QIcon("red.png"))
    def UnsetAlert(self):
        self.trayIcon.setIcon(QtGui.QIcon("green.png"))
    def UpdateData(self):
        Update(self,self.conf)
    def ShowAbout(self):
        webbrowser.open_new_tab(os.path.join(os.getcwd(),self.conf.aboutfile))
    def ShowLast(self):
        Update(self,self.conf)
        Handler(self," ",self.conf).ShowLast(self,self.conf)
    def closeEvent(self,e):
        e.accept()
        app.exit()

class TerminalX(QtCore.QThread):
    def __init__(self,parent=None):
        QtCore.QThread.__init__(self,parent)

    def run(self):
        global timeout
        #while True:
            #time.sleep(timeout)
            #self.emit(QtCore.SIGNAL("UpdateData()"))
            #print "################################################"


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
