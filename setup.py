import sys
from distutils.core import setup
import py2exe
from distutils.core import setup
import py2exe

MyData_Files = ['config.cfg','green.png','red.png','yellow.png',
                'anim.gif','About.html',
                'fliph.js','pixastic.core.js','rotate.js']


setup(windows=[{"script":"GA.py"}],
      options={"py2exe":{"includes":["sip","lxml.etree","lxml._elementpath","gzip"]}},
      data_files = MyData_Files
     )
