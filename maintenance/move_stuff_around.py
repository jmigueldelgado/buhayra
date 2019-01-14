import os
from buhayra.getpaths import *
import sys
def rename_json():
    while(selectPattern(sarOut,'orrjson$')):
        f=selectPattern(sarOut,'orrjson$')
        os.rename(sarOut+'/'+f,sarOut+'/'+f[:-4]+'.json')

def move_proc():
    Y=int(sys.argv[1])
    M=int(sys.argv[2])
    timestamp=list()
    for tif in listdir(procOut):
        if  not tif.startswith('S'):
            continue
        stamp=datetime.datetime.strptime(tif.split('_')[4],'%Y%m%dT%H%M%S')
        if re.search('.tif$',tif) and stamp.year==Y and stamp.month==M:
            timestamp.append(stamp)
            if os.isfile(sarOut+'/'+tif):
                # os.remove(sarOut+'/'+tif)
                continue
            os.rename(procOut + '/' + tif,sarOut+'/'+tif)
            open(sarOut+'/'+f[:-3]+'finished','w').close()
    if(len(timestamp)<1):
        logger.info(procOut+" has no tiffs for year "+str(Y)+" and month "+str(M)+"Exiting.")
