import sys
from distutils.core import setup
import py2exe
from distutils.core import setup
import py2exe

MyData_Files = ['Gg.png','green.png','Gr.png','Gy.png','red.png','yellow.png','About.html']


setup(windows=[{"script":"GA.py"}],
      options={"py2exe":{"includes":["sip","lxml.etree","lxml._elementpath","gzip"]}},
      data_files = MyData_Files
     )
