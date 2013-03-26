from distutils.core import setup
import py2app

NAME = 'Cartel'
SCRIPT = 'cartel.py'
VERSION = '0.4.3'
ID = 'cartel'

plist = dict(
     CFBundleName                = NAME,
     CFBundleShortVersionString  = ' '.join([NAME, VERSION]),
     CFBundleGetInfoString       = NAME,
     CFBundleExecutable          = NAME,
     CFBundleIdentifier          = 'org.jmatt.%s' % ID,
     LSUIElement                 = '1', #makes it not appear in cmd-tab task list etc.
)

app_data = dict(script=SCRIPT, plist=plist)

setup(
   app = [app_data],
   options = {
       'py2app':{
           'resources':[
               ],
           'excludes':[
               ],
           'includes':[
             'mechanize'
               ],
           'iconfile':
             'Coffee Cup Icon Black.icns'
           },
       },
   data_files=['coffee+cup+icon+black.png', 'Coffee Cup Icon Black.icns']
)
