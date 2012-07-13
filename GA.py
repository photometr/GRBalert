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
from datetime import datetime
import webbrowser
from GenHTML import GenHTML
import threading
import router
import voevent
import config
import gcn
import log

def startThreads(TerminalViewerInstance,StopThreadFlag):
   voeventthread = threading.Thread(name='voserver', target=voevent.voserver_thread, args=(TerminalViewerInstance,StopThreadFlag))
   voeventthread.start()
   routerthread = threading.Thread(name='router', target=router.gcn_thread, args=(TerminalViewerInstance,StopThreadFlag))
   routerthread.start()

class TerminalViewer(QtGui.QWidget):
    def __init__(self,app,parent=None):
        self.conf = config.Config()
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
        self.exitAction.connect(self.exitAction, SIGNAL("triggered()"), self.closeEvent)
        self.resetAction.connect(self.resetAction, SIGNAL("triggered()"), self.UnsetAlert)
        self.aboutAction.connect(self.aboutAction, SIGNAL("triggered()"), self.ShowAbout)
        self.lastAction.connect(self.lastAction, SIGNAL("triggered()"), self.ShowLast)
        self.connect(self.DataCollector,QtCore.SIGNAL("UpdateData() "), self.UpdateData)
        self.StopThreadFlag = [False]
        startThreads(self,self.StopThreadFlag)
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
        fop = open("latest_grb_packet.xml",'r')
        xml = fop.read()
        fop.close()
        gcnh = gcn.GCNHandler(self,xml,self.conf,True)
    def closeEvent(self):
        self.StopThreadFlag[0] = True
        QtGui.qApp.quit()


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
    log.init()
    app = QtGui.QApplication(sys.argv)
    qb = TerminalViewer(app)
    main_window = MainWindow(qb)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
