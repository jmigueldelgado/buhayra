from functools import partial
import pyproj
import os
import logging
import re
from buhayra.getpaths import *
from shapely.ops import transform
from shapely.geometry import Polygon, shape, Point
from datetime import date, datetime, timedelta

def raster2rect(raster):
    pointlist=list()
    pointlist.append(Point(raster.bounds.left,raster.bounds.bottom))
    pointlist.append(Point(raster.bounds.left,raster.bounds.top))
    pointlist.append(Point(raster.bounds.right,raster.bounds.top))
    pointlist.append(Point(raster.bounds.right,raster.bounds.bottom))
    pointlist.append(Point(raster.bounds.left,raster.bounds.bottom))

    return Polygon([[p.x, p.y] for p in pointlist])


def getWMinScene(rect,wm):
    wm_in_scene=list()
    id=list()
    for feat in wm:
        pol=geojson2shapely(feat['geometry'])
        pol=checknclean(pol)
        if rect.contains(pol):
            wm_in_scene.append(pol)
            id.append(feat['properties']['id_jrc'])
    return(wm_in_scene,id)

def checknclean(pol):
    if not pol.is_valid:
        clean=pol.buffer(0)
        return(clean)
    else:
        return(pol)

def geojson2shapely(jsgeom):
    polygon=shape(jsgeom)
    return(polygon)

def select_scene_ingestion_time(ingestion_time,src_path):
    logger = logging.getLogger('root')

    subs=datetime.strftime(ingestion_time,'%Y%m%dT%H%M%S')
    res = [x for x in os.listdir(src_path) if re.search(subs, x.split('_')[4]) and x.endswith('.zip')]

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
            stamp=datetime.strptime(scn.split('_')[4],'%Y%m%dT%H%M%S')
            if re.search('.zip$',scn) and stamp.year==Y and stamp.month==M:
                scenes_in_ym.append(scn)
                timestamp.append(stamp)
        if(len(timestamp)<1):
            logger.info(src_path+" has no scene for year "+Y+" and month "+M+"Exiting and returning None.")
            scenes_in_ym=None
    return(scenes_in_ym)

def select_last_scene(src_path):
    logger = logging.getLogger('root')
    timestamp=list()
    scenes=list()
    for scn in os.listdir(src_path):
        if re.search('.zip$',scn):
            if os.path.isfile(os.path.join(src_path,scn[:-3]+'finished')) or os.path.isfile(os.path.join(src_path,scn[:-3]+'processing')):
                continue
            scenes.append(scn)
            timestamp.append(datetime.strptime(scn.split('_')[4],'%Y%m%dT%H%M%S'))
    if len(scenes)>0:
        f=scenes[timestamp.index(max(timestamp))]
    else:
        f=[]
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
            stamp=datetime.strptime(scn.split('_')[4],'%Y%m%dT%H%M%S')
            if re.search('.zip$',scn) and stamp.year==Y and stamp.month==M:
                scenes_in_ym.append(scn)
                timestamp.append(stamp)
        if(len(timestamp)<1):
            logger.info(src_path+" has no scene for year "+Y+" and month "+M+"Exiting and returning None.")
            f=None
        else:
            f=scenes_in_ym[timestamp.index(max(timestamp))]
    return(f)

###### get tifs by year and month

def select_folders_year_month(Y,M,src_path):
    logger = logging.getLogger('root')
    timestamp=list()
    allfolders = [ name for name in os.listdir(src_path) if os.path.isdir(os.path.join(src_path, name)) ]
    folders_in_ym=list()

    for folder in allfolders:
        stamp=datetime.strptime(folder.split('_')[4],'%Y%m%dT%H%M%S')
        if stamp.year==Y and stamp.month==M:
            folders_in_ym.append(os.path.join(src_path,folder))
            if not os.path.exists(os.path.join(edgeOut,folder)):
                os.mkdir(os.path.join(edgeOut,folder))
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
                stamp=datetime.strptime(tif.split('_')[4],'%Y%m%dT%H%M%S')
                if re.search('.tif$',tif) and stamp.year==Y and stamp.month==M:
                    tiffs_in_ym.append(os.path.join(searchDir,tif))
    if(len(tiffs_in_ym)<1):
        logger.info("The selected folders have no tiffs for year "+str(Y)+" and month "+str(M)+"Exiting and returning None.")
        tiffs_in_ym=None
    return(tiffs_in_ym)

###### get tifs of the last 7 days

def select_folders_7days(src_path):
    logger = logging.getLogger('root')
    timestamp=list()
    allfolders = [ name for name in os.listdir(src_path) if os.path.isdir(os.path.join(src_path, name)) ]
    folders_in_7days=list()

    for folder in allfolders:
        stamp=datetime.strptime(folder.split('_')[4],'%Y%m%dT%H%M%S')
        if (datetime.now() - stamp) < timedelta(days=7):
            folders_in_7days.append(os.path.join(src_path,folder))
    if(len(folders_in_7days)<1):
        logger.info(src_path+" has no processed scenes in the last 7 days. Exiting and returning empty list. Check if sar2watermask is working properly.")
    return folders_in_7days


def select_tiffs_7days(folders_in_7days):
    logger = logging.getLogger('root')
    tiffs_in_7days=list()
    if len(folders_in_7days)<1:
        pass
    else:
        for searchDir in folders_in_7days:
            for tif in os.listdir(searchDir):
                if  os.path.isfile(os.path.join(searchDir,tif[:-3]+'finished')) or not tif.startswith('S'):
                    continue
                if re.search('.tif$',tif):
                    tiffs_in_7days.append(os.path.join(searchDir,tif))
    if(len(tiffs_in_7days)<1):
        logger.info("The selected folders have no unprocessed tiffs for the last 7 days. Exiting and returning an empty list.")
    return tiffs_in_7days

def list_scenes_finished(src_path):
    logger = logging.getLogger('root')

    scenes_finished=list()

    if(len(os.listdir(src_path))<1):
        logger.info('No scenes found in '+ src_path +'. Exiting and returning an empty list.')
    else:
        for scn in os.listdir(src_path):
            stamp=datetime.strptime(scn.split('_')[4],'%Y%m%dT%H%M%S')
            if re.search('.finished$',scn)  and (datetime.now() - stamp) > timedelta(days=7):
                scenes_finished.append(scn)
        if(len(scenes_finished)<1):
            logger.info("No finished scenes found in " + src_path + ". Exiting and returning an empty list.")
        else:
            logger.info(str(len(scenes_finished))+" finished scenes found in " + src_path)
    return(scenes_finished)


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
