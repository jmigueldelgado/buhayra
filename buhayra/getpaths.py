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

vegdir = scratch + "/vegetated_water_surfaces"
sardir=scratch+"/s1a_scenes"
s2adir=scratch+"/s2a_scenes"

s2aIn=s2adir+"/in"
s2aIn=s2adir+"/in"
s2aOut=s2adir+"/out"

vegIn = vegdir + "/in"
vegOut = vegdir + "/out"

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

def select_tiffs_year_month(Y,M,folders_in_ym):
    logger = logging.getLogger('root')
    tiffs_in_ym=list()

    if folders_in_ym is None:
        pass
    else:
        for folder in folders_in_ym:
            searchDir = os.path.join(folder,folder)
            for tif in listdir(searchDir):
                if  os.path.isfile(searchDir+'/'+tif[-3]+'finished') or not tif.startswith('S'):
                    continue
                stamp=datetime.datetime.strptime(tif.split('_')[4],'%Y%m%dT%H%M%S')
                if re.search('.tif$',tif) and stamp.year==Y and stamp.month==M:
                    tiffs_in_ym.append(os.path.join(folder,tif))
    if(len(tiffs_in_ym)<1):
        logger.info("The selected folders have no tiffs for year "+str(Y)+" and month "+str(M)+"Exiting and returning None.")
        tiffs_in_ym=None
    return(tiffs_in_ym)

def select_folders_year_month(Y,M,src_path):
    logger = logging.getLogger('root')
    timestamp=list()
    allfolders = [ name for name in os.listdir(src_path) if os.path.isdir(os.path.join(src_path, name)) ]
    folders_in_ym=list()

    for folder in allfolders:
        stamp=datetime.datetime.strptime(folder.split('_')[4],'%Y%m%dT%H%M%S')
        if stamp.year==Y and stamp.month==M:
            folders_in_ym.append(folder)
    if(len(folders_in_ym)<1):
        logger.info(src_path+" has no scenes for year "+str(Y)+" and month "+str(M)+"Exiting and returning None.")
        folders_in_ym=None
    return folders_in_ym




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
