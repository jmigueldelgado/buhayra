import os
from buhayra.getpaths import *
import buhayra.utils as utils
import logging
import shapely
from shapely.geometry import mapping, Polygon, shape
from shapely.ops import cascaded_union, transform
import datetime
import json
import numpy as np
import geojson

def load_metadata(f):
    with open(polOut+'/'+f[:-3]+'json', 'r') as fjson:
        metadata = json.load(fjson)
    return metadata



def select_intersecting_polys(geom,refgeoms,f):
    # split extension and get parts of filename containing metadata
    metalist=os.path.splitext(f)[0].split('_')

    geom=utils.wgs2utm(geom.buffer(0))

    refgeom = refgeoms[int(metalist[9])]

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
    metalist=os.path.splitext(f)[0].split('_')
    sentx=metalist[0]
    if np.isnan(thr):
        thr=0
    props={
        'source_id':sentx,
        'ingestion_time':datetime.datetime.strptime(metalist[4],'%Y%m%dT%H%M%S'),
        'id_jrc':int(metalist[9]),
        'threshold':thr,
        'wmXjrc_area':intersection_area,}

    poly_wgs=utils.utm2wgs(poly.buffer(0))

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
    logger = logging.getLogger('root')
    feats=[]
    for dict in ls:
        if type(dict['properties']['ingestion_time']) == datetime.datetime:
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
