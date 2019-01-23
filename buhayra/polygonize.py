import os
from buhayra.getpaths import *
import logging
import rasterio
from rasterio import features
import shapely
from shapely.geometry import mapping, Polygon, shape
from shapely.ops import cascaded_union, transform
import fiona
import datetime
import json
from functools import partial
import pyproj
import numpy as np
import geojson

def load_metadata(f):
    with open(polOut+'/'+f[:-3]+'json', 'r') as fjson:
        metadata = json.load(fjson)
    return metadata

def load_watermask(f):
    with rasterio.open(polOut+'/'+f,'r') as ds:
        ds.profile.update(dtype=rasterio.int32)
        r=ds.read(1)
    return r

def raster2shapely(r,metadata):
    affParam=rasterio.Affine.from_gdal(metadata[0],metadata[1],metadata[2],metadata[3],metadata[4],metadata[5])
    polys=list()
    for pol, value in features.shapes(r, transform=affParam):
        if value==1:
            polys.append(shape(pol))
    return cascaded_union(polys)


def select_intersecting_polys(geom,wm,f):
    metalist=f[:-4].split('_')

    project = partial(
        pyproj.transform,
        pyproj.Proj(init='epsg:4326'),
        pyproj.Proj(init='epsg:32724'))

    geom=geom.buffer(0)
    geom=transform(project,geom)


    ## replace this with some kind of `find`
    for wm_feat in wm:
        if int(wm_feat['id'])==int(metalist[9]):
            refgeom=shape(wm_feat['geometry'])
            refgeom=refgeom.buffer(0)
            break

    inters=list()
    if geom.geom_type == 'MultiPolygon':
        for poly in geom:
            if poly.intersects(refgeom):
                inters.append(poly)
        if len(inters)>0:
            geom_out = cascaded_union(inters)
            # s=json.dumps(mapping(inters))
            # feat['geometry']=json.loads(s)
        else:
            geom_out=Polygon().buffer(0)
    elif geom.geom_type == 'Polygon':
        if geom.intersects(refgeom):
            geom_out=geom
            # s=json.dumps(mapping(geom))
            # feat['geometry']=json.loads(s)
        else:
            geom_out=Polygon().buffer(0)

    xgeom = refgeom.intersection(geom_out)

    return geom_out, xgeom.area

def prepareDict(poly,f,thr,intersection_area):
    metalist=f[:-4].split('_')
    sentx=metalist[0]
    if np.isnan(thr):
        thr=0
    props={
        'source_id':sentx[1],
        'ingestion_time':datetime.datetime.strptime(metalist[4],'%Y%m%dT%H%M%S'),
        'id_jrc':int(metalist[9]),
        'threshold':thr,
        'wmxjrc_area':intersection_area,}

    project = partial(
        pyproj.transform,
        pyproj.Proj(init='epsg:32724'),
        pyproj.Proj(init='epsg:4326'))

    poly=poly.buffer(0)

    poly_wgs=transform(project,poly)

    s=json.dumps(mapping(poly_wgs))
    geom=json.loads(s)


    feat={
        'type':'Feature',
        'properties':props,
        'geometry':geom
        }
    feat['properties']['area']=poly.area

    return feat


def json2geojson(ls):
    feats=[]
    for dict in ls:
        dttm=dict['properties']['ingestion_time']
        dttmstr=dttm.strftime("%Y-%m-%d %H:%M:%S")
        dict['properties']['ingestion_time']=dttmstr

        if dict['geometry'] is None or len(dict['geometry']['coordinates'])==0:
            feats.append(geojson.Feature(geometry=None,properties=dict['properties']))
        else:
            ## mixing poly and multipoly is not accepted by postgis. we will force Polygon into MultiPolygon
            mp=geojson.MultiPolygon()

            ## now we have to correct syntax of MultiPolygon which was forced from Polygon so it generates valid geojson in the end
            if dict["geometry"]["type"]=='Polygon':
                dict["geometry"]["coordinates"]=[dict["geometry"]["coordinates"]]
            #if len(poly['geometry']['coordinates'])==1:
            #    mp=geojson.Polygon()

            mp['coordinates']=dict['geometry']['coordinates']
            feats.append(geojson.Feature(geometry=mp,properties=dict['properties']))



    return geojson.FeatureCollection(feats)


def remove_watermask(f,feat_id):
    logger = logging.getLogger('root')
    os.remove(polOut+'/'+f[:-3]+'json')
    os.remove(polOut + '/' + f)
    return f

def wgs2utm(geom):
    project = partial(
        pyproj.transform,
        pyproj.Proj(init='epsg:4326'),
        pyproj.Proj(init='epsg:32724'))
    geom_utm=transform(project,geom)
    return(geom_utm)


def select_tiffs_year_month(Y,M):
    logger = logging.getLogger('root')

    if(len(listdir(polOut))<1):
        logger.info(polOut+" is empty! Nothing to do. Exiting and returning None.")
        tiffs_in_ym=None
    else:
        timestamp=list()
        tiffs_in_ym=list()
        for tif in listdir(polOut):
            if not tif.startswith('S'):
                continue
            stamp=datetime.datetime.strptime(tif.split('_')[4],'%Y%m%dT%H%M%S')
            if re.search('.tif$',tif) and stamp.year==Y and stamp.month==M:
                tiffs_in_ym.append(tif)
                timestamp.append(stamp)
        if(len(timestamp)<1):
            logger.info(polOut+" has no tiffs for year "+str(Y)+" and month "+str(M)+"Exiting and returning None.")
            tiffs_in_ym=None
    return(tiffs_in_ym)

def select_n_last_tiffs(n):
    logger = logging.getLogger('root')

    if(len(listdir(polOut))<1):
        logger.info(polOut+" is empty! Nothing to do. Exiting and returning None.")
        tiffs=None
    else:
        timestamp=list()
        tiffs=list()
        for tiff in listdir(polOut):
            if not tiff.startswith('S'):
                continue
            stamp=datetime.datetime.strptime(tiff.split('_')[4],'%Y%m%dT%H%M%S')
            if re.search('.tif$',tiff):
                tiffs.append(tiff)
                timestamp.append(stamp)

        if(len(timestamp)<1):
            logger.info(polOut+"Has not tifs. Exiting and returning None.")
            tiffs.append(None)
        if(len(timestamp)<=n):
            return(tiffs)
        else:
            index=np.argsort(timestamp)
            return([tiffs[i] for i in index[-n:]])
    return(tiffs)
