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
        if scene.endswith('.finished'):
            continue
        if not os.path.isdir(os.path.join(sarOut,scene[:-4])):
            os.mkdir(os.path.join(sarOut,scene[:-4]))
        if not os.path.isdir(os.path.join(procOut,scene[:-4])):
            os.mkdir(os.path.join(procOut,scene[:-4]))
        for filename in outtifs:
            if filename.startswith(scene[:-4]) and (filename.endswith('.tif') or filename.endswith('.json') or filename.endswith('.finished')):
                src = os.path.join(sarOut,filename)
                trg = os.path.join(sarOut,scene[:-4],filename)
                os.rename(src,trg)
        for filename in proctifs:
            if filename.startswith(scene[:-4]) and (filename.endswith('.tif') or filename.endswith('.json') or filename.endswith('.finished')):
                src = os.path.join(procOut,filename)
                trg = os.path.join(procOut,scene[:-4],filename)
                os.rename(src,trg)
