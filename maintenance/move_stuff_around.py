import os
from buhayra.getpaths import *
import datetime
import re
from buhayra.getpaths import *

def rename_json():
    while(selectPattern(sarOut,'orrjson$')):
        f=selectPattern(sarOut,'orrjson$')
        os.rename(sarOut+'/'+f,sarOut+'/'+f[:-4]+'.json')

def move_proc(Y,M):
    folders = select_folders_year_month(Y,M,procOut)
    for folder in folders:
        if  not folder.startswith('S'):
            continue
        if not os.path.isdir(os.path.join(procOut,folder)):
            continue
        for filename in os.listdir(os.path.join(procOut,folder)):
            if filename.endswith('.tif'):
                if not os.path.isfile(os.path.join(sarOut,folder,filename)):
                    os.rename(os.path.join(procOut,folder,filename),os.path.join(sarOut,folder,filename))
                if not os.path.exists(os.path.join(sarOut,folder,filename[:-3]+'finished')):
                    open(os.path.join(sarOut,folder,filename[:-3]+'finished','w')).close()
            if filename.endswith('.json'):
                if not os.path.isfile(os.path.join(sarOut,folder,filename')):
                    os.rename(os.path.join(procOut,folder,filename),os.path.join(sarOut,folder,filename))


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
