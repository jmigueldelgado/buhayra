from os.path import expanduser,exists
import sys
import socket
from os import listdir
import re
import logging

if socket.gethostname()=='vouga':
    home = {
        'home' : expanduser("~"),
        'scratch' : expanduser("~") + '/scratch',
        'proj' : expanduser("~") + '/proj/buhayra',
        'parameters' : expanduser("~") + '/proj/buhayra/buhayra/parameters'}
elif socket.gethostname()=='compute':
    home = {
        'home' : expanduser("~"),
        'scratch' : expanduser("~") + '/scratch',
        'proj' : expanduser("~") + '/proj/buhayra',
        'parameters' : expanduser("~") + '/proj/buhayra/buhayra/parameters'}
elif socket.gethostname()=='ubuntuserver':
    home = {
        'home' : expanduser("~"),
        'scratch' : 'None',
        'proj' : expanduser("~") + '/proj/buhayra',
        'parameters' : expanduser("~") + '/proj/buhayra/buhayra/parameters'}
elif socket.gethostname()=='MEKONG':
    home = {
        'home' : expanduser("~"),
        'scratch' : expanduser("~") + '/scratch',
        'proj' : expanduser("~") + '/proj/buhayra',
        'parameters' : expanduser("~") + '/proj/buhayra/buhayra/parameters'}
elif socket.gethostname()=='vm-sesam':
    home = {
        'home' : expanduser("~"),
        'scratch' : expanduser("~") + '/SESAM/sesam_share/delgado/scratch',
        'proj' : expanduser("~") + '/proj/buhayra',
        'parameters' : expanduser("~") + '/proj/buhayra/buhayra/parameters'}
else:
    home = {
        'home' : expanduser("~"),
        'scratch' : '/mnt/scratch/martinsd',
        'proj' : expanduser("~") + '/proj/buhayra',
        'parameters' : expanduser("~") + '/proj/buhayra/buhayra/parameters'}


proj = home['proj']
scratch= home['scratch']


sardir=scratch+"/s1a_scenes"
s2adir=scratch+"/s2a_scenes"

s2aIn=s2adir+"/in"
s2aIn=s2adir+"/in"
s2aOut=s2adir+"/out"

sarIn=sardir+"/in"
sarOut=sardir+"/out"

polOut=scratch + "/watermasks"
procOut=scratch + "/processed_watermasks"

MONGO_HOST = "141.89.96.184"
MONGO_DB = "sar2watermask"
MONGO_PORT = 27017

orbits_url = 'http://aux.sentinel1.eo.esa.int/RESORB/'


sys.path.insert(0, home['parameters'])

if exists(home['proj']+'/buhayra/credentials.py'):
    from buhayra.credentials import *

def selectTiff(dir):
    logger = logging.getLogger('root')
    if(len(listdir(dir))<1):
        logger.info(dir+" is empty! Nothing to do. Exiting and returning None.")
        return False
    l=listdir(dir)
    for s in l:
        if re.search('.tif$',s):
            return(s)
    return False

def selectPattern(dir,pattern):
    logger = logging.getLogger('root')
    if(len(listdir(dir))<1):
        logger.info(dir+" is empty! Nothing to do. Exiting and returning None.")
        return False
    l=listdir(dir)
    for s in l:
        if re.search(pattern,s):
            return(s)
    return False
