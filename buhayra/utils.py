from functools import partial
import pyproj
import os
import logging
import re
import datetime
from buhayra.getpaths import *
from shapely.ops import transform

def select_scene_ingestion_time(ingestion_time,src_path):
    logger = logging.getLogger('root')

    subs=datetime.datetime.strftime(ingestion_time,'%Y%m%dT%H%M%S')
    res = [x for x in os.listdir(src_path) if re.search(subs, x.split('_')[4])]

    return res


def select_scenes_year_month(Y,M,src_path):
    logger = logging.getLogger('root')

    if(len(os.listdir(src_path))<1):
        logger.info(src_path+" is empty! Nothing to do. Exiting and returning None.")
        scenes_in_ym=None
    else:
        timestamp=list()
        scenes_in_ym=list()
        for scn in os.listdir(src_path):
            stamp=datetime.datetime.strptime(scn.split('_')[4],'%Y%m%dT%H%M%S')
            if re.search('.zip$',scn) and stamp.year==Y and stamp.month==M:
                scenes_in_ym.append(scn)
                timestamp.append(stamp)
        if(len(timestamp)<1):
            logger.info(src_path+" has no scene for year "+Y+" and month "+M+"Exiting and returning None.")
            scenes_in_ym=None
    return(scenes_in_ym)

def select_last_scene(src_path):
    logger = logging.getLogger('root')
    if(len(os.listdir(src_path))<1):
        logger.info(src_path+" is empty! Nothing to do. Exiting and returning None.")
        f=None
    else:
        timestamp=list()
        scenes=list()
        for scn in os.listdir(src_path):
            if re.search('.zip$',scn):
                scenes.append(scn)
                timestamp.append(datetime.datetime.strptime(scn.split('_')[4],'%Y%m%dT%H%M%S'))
        f=scenes[timestamp.index(max(timestamp))]
    return(f)


def select_past_scene(Y,M,src_path):
    logger = logging.getLogger('root')

    if(len(os.listdir(src_path))<1):
        logger.info(src_path+" is empty! Nothing to do. Exiting and returning None.")
        f=None
    else:
        timestamp=list()
        scenes_in_ym=list()
        for scn in os.listdir(src_path):
            stamp=datetime.datetime.strptime(scn.split('_')[4],'%Y%m%dT%H%M%S')
            if re.search('.zip$',scn) and stamp.year==Y and stamp.month==M:
                scenes_in_ym.append(scn)
                timestamp.append(stamp)
        if(len(timestamp)<1):
            logger.info(src_path+" has no scene for year "+Y+" and month "+M+"Exiting and returning None.")
            f=None
        else:
            f=scenes_in_ym[timestamp.index(max(timestamp))]
    return(f)


def select_folders_year_month(Y,M,src_path):
    logger = logging.getLogger('root')
    timestamp=list()
    allfolders = [ name for name in os.listdir(src_path) if os.path.isdir(os.path.join(src_path, name)) ]
    folders_in_ym=list()

    for folder in allfolders:
        stamp=datetime.datetime.strptime(folder.split('_')[4],'%Y%m%dT%H%M%S')
        if stamp.year==Y and stamp.month==M:
            folders_in_ym.append(os.path.join(src_path,folder))
    if(len(folders_in_ym)<1):
        logger.info(src_path+" has no scenes for year "+str(Y)+" and month "+str(M)+"Exiting and returning None.")
        folders_in_ym=None
    return folders_in_ym

def select_tiffs_year_month(Y,M,folders_in_ym):
    logger = logging.getLogger('root')
    tiffs_in_ym=list()

    if folders_in_ym is None:
        pass
    else:
        for searchDir in folders_in_ym:
            for tif in os.listdir(searchDir):
                if  os.path.isfile(os.path.join(searchDir,tif[-3]+'finished')) or not tif.startswith('S'):
                    continue
                stamp=datetime.datetime.strptime(tif.split('_')[4],'%Y%m%dT%H%M%S')
                if re.search('.tif$',tif) and stamp.year==Y and stamp.month==M:
                    tiffs_in_ym.append(os.path.join(searchDir,tif))
    if(len(tiffs_in_ym)<1):
        logger.info("The selected folders have no tiffs for year "+str(Y)+" and month "+str(M)+"Exiting and returning None.")
        tiffs_in_ym=None
    return(tiffs_in_ym)


def selectPattern(dir,pattern):
    logger = logging.getLogger('root')
    if(len(os.listdir(dir))<1):
        logger.info(dir+" is empty! Nothing to do. Exiting and returning None.")
        return False
    l=os.listdir(dir)
    for s in l:
        if re.search(pattern,s):
            return(s)
    return False


def wgs2utm(geom):
    project = partial(
        pyproj.transform,
        pyproj.Proj(init='epsg:4326'),
        pyproj.Proj(init=location['utm']))
    geom_utm=transform(project,geom)
    return(geom_utm)

def utm2wgs(geom):
    project = partial(
        pyproj.transform,
        pyproj.Proj(init=location['utm']),
        pyproj.Proj(init='epsg:4326'))
    geom_wgs=transform(project,geom)
    return(geom_wgs)
