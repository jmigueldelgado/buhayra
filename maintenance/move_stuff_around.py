import os
from buhayra.getpaths import *
import sys
import datetime

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
