import os
from buhayra.getpaths import *
import datetime
import re

def rename_json():
    while(selectPattern(sarOut,'orrjson$')):
        f=selectPattern(sarOut,'orrjson$')
        os.rename(sarOut+'/'+f,sarOut+'/'+f[:-4]+'.json')

def move_proc(Y,M):
    timestamp=list()
    for tif in os.listdir(procOut):
        if  not tif.startswith('S'):
            continue
        stamp=datetime.datetime.strptime(tif.split('_')[4],'%Y%m%dT%H%M%S')
        if re.search('.tif$',tif) and stamp.year==Y and stamp.month==M:
            timestamp.append(stamp)
            if os.path.isfile(sarOut+'/'+tif):
                # os.remove(sarOut+'/'+tif)
                continue
            os.rename(procOut + '/' + tif,sarOut+'/'+tif)
            open(sarOut+'/'+tif[:-3]+'finished','w').close()

def move_tifs_to_folders():
    scenes=os.listdir(sarIn)
    outtifs = os.listdir(sarOut)
    proctifs = os.listdir(procOut)
    for scene in scenes:
        os.mkdir(os.path.join(sarOut,scene[:-4]))
        os.mkdir(os.path.join(procOut,scene[:-4]))
        for filename in outtifs:
            if re.search(scene[:-4],filename):
                src = os.path.join(sarOut,filename)
                trg = os.path.join(sarOut,scene[:-4],filename)
                os.rename(src,trg)
        for filename in proctifs:
            if re.search(scene[:-4],filename):
                src = os.path.join(procOut,filename)
                trg = os.path.join(procOut,scene[:-4],filename)
                os.rename(src,trg)
