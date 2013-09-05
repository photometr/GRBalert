#configuration file handling
import ConfigParser

class Config():
    def __init__(self):
      config = ConfigParser.RawConfigParser()
      config.read('config.cfg')

      self.longitude = config.getfloat('location', 'longitude')
      self.latitude = config.getfloat('location', 'latitude')
      self.altitude = config.getfloat('location', 'altitude')
      self.coorerr = config.getfloat('location', 'coorerr')
      self.is_utc  = config.getbool('location', 'is_utc')
      self.alt_limit = config.getfloat('GRBparams', 'alt_limit')
      self.htmlfile = config.get('info', 'htmlfile')
      self.aboutfile = config.get('info', 'aboutfile')
      self.usefermi = config.getboolean('scanparams', 'usefermi')
      self.socketip = config.get('scanparams', 'socketip')
      self.socketport = config.getint('scanparams', 'socketport')
      self.datalength = config.getint('scanparams', 'datalength')
      self.voeventport = config.getint('scanparams', 'voeventport')
      self.voeventips = self.get(config, 'scanparams', 'voeventips')
    def get(self, config, section, option):
      """ Get a parameter if the returning value is a list,
                      convert string value to a python list"""
      value = config.get(section, option)
      if (value[0] == "[") and (value[-1] == "]"):
	#WARNING not safe
	return eval(value)
      else:
        return value
