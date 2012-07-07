#class for VO event
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
        self.types = { #51  : "TEST",##############################
	               53  : "INTEGRAL_WAKEUP",
                       #54  : "INTEGRAL_REFINED",##############################
                       #55  : "INTEGRAL_OFFLINE",##############################
                       61  : "SWIFT_BAT_GRB_POS",
                       67  : "SWIFT_XRT_POS",
                       81  : "SWIFT_UVOT_POS",
                       #82  : "SWIFT_BAT_GRB_POS_TEST",##############################
                       #83  : "TEST",##############################
                       101 : "SuperAGILE_GRB_POS_GROUND",
                       102 : "SuperAGILE_GRB_POS_REFINED",
                       #109 : "AGILE_GRB_POS_TEST",##################################
                       112 : "FERMI_GBM_GND_POS",
                       #119 : "FERMI_GBM_GRB_POS_TEST",#############################
                       #124 : "FERMI_LAT_GRB_POS_TEST",##############################
                       134 : "MAXI_UNKNOWN_SOURCE",
                       #136 : "MAXI_TEST",#######################################
                       #140 : "TEST",#######################################
                       #141 : "TEST",#######################################
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

