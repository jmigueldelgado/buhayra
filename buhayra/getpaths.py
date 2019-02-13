from os.path import expanduser,exists
import sys
import socket
import yaml
import os
### add your hostname and things will run smoothly

if socket.gethostname()=='vouga':
    home = {
        'home' : expanduser("~"),
        'scratch' : expanduser("~") + '/scratch'}
elif socket.gethostname()=='compute':
    home = {
        'home' : expanduser("~"),
        'scratch' : expanduser("~") + '/scratch'}
elif socket.gethostname()=='ubuntuserver':
    home = {
        'home' : expanduser("~"),
        'scratch' : 'None'}
elif socket.gethostname()=='MEKONG':
    home = {
        'home' : expanduser("~"),
        'scratch' : expanduser("~") + '/scratch'}
else:
    home = {
        'home' : expanduser("~"),
        'scratch' : '/mnt/scratch/martinsd'}

home['parameters'] = os.path.join(home['proj'],'buhayra','parameters')

with open(os.path.join(home['parameters'],'location.yml'), 'r') as stream:
    location=yaml.load(stream)

home['proj'] =os.path.join(home['home'],'proj','buhayra'+'_'+location['region'])
home['scratch'] =home['scratch']+'_'+location['region']

sardir=os.path.join(home['scratch'],'s1a_scenes')

sarIn=os.path.join(sardir,'in')
sarOut=os.path.join(sardir,'out')

polOut = os.path.join(home['scratch'],'watermasks')
procOut = os.path.join(home['scratch'],'processed_watermasks')

orbits_url = 'http://aux.sentinel1.eo.esa.int/RESORB/'

# sys.path.insert(0, home['parameters'])



if exists(os.path.join(home['proj'],'buhayra','credentials.py')):
    from buhayra.credentials import *
