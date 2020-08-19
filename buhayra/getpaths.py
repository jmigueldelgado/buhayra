from os.path import expanduser,exists
import sys
import socket
import os
from buhayra.location import *
### add your hostname and things will run smoothly

if socket.gethostname()=='vouga':
    home = {
        'home' : expanduser("~"),
        'scratch' : os.path.join(expanduser("~"), 'scratch')}
elif socket.gethostname()=='compute':
    home = {
        'home' : expanduser("~"),
        'scratch' : os.path.join(expanduser("~"), 'scratch')}
elif socket.gethostname()=='ubuntuserver':
    home = {
        'home' : expanduser("~"),
        'scratch' : 'None'}
elif socket.gethostname()=='MEKONG':
    home = {
        'home' : expanduser("~"),
        'scratch' : os.path.join(expanduser("~"), 'scratch')}
else:
    home = {
        'home' : expanduser("~"),
        'scratch' : '/mnt/scratch/martinsd'}

if location['region']==None:
    home['proj'] =os.path.join(home['home'],'proj','buhayra')
else:
    home['proj'] =os.path.join(home['home'],'proj','buhayra'+'_'+location['region'])
    home['scratch'] = home['scratch']+'_'+location['region']


home['parameters'] = os.path.join(home['proj'],'buhayra','parameters')
sardir=os.path.join(home['scratch'],'s1a_scenes')

sarIn=os.path.join(sardir,'in')
sarOut=os.path.join(sardir,'out')

dirDEMs=os.path.join(home['scratch'],'dem')

polOut = os.path.join(home['scratch'],'watermasks')
procOut = os.path.join(home['scratch'],'processed_watermasks')

orbits_url = 'http://aux.sentinel1.eo.esa.int/RESORB/'

# sys.path.insert(0, home['parameters'])



if exists(os.path.join(home['proj'],'buhayra','credentials.py')):
    from buhayra.credentials import *
