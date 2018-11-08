import os
from buhayra.getpaths import *
import logging
import rasterio
from rasterio import features
import shapely
from shapely.geometry import shape
from shapely.geometry import mapping
from shapely.ops import cascaded_union, transform
import fiona
import datetime
import json
from functools import partial
import pyproj


def tif2shapely(f):
    ds=rasterio.open(polOut+'/'+f,'r')
    # ds.profile.update(dtype=rasterio.int32)
    with open(polOut+'/'+f[:-3]+'json', 'r') as fjson:
        gdalParam = json.load(fjson)
    affParam=rasterio.Affine.from_gdal(gdalParam[0],gdalParam[1],gdalParam[2],gdalParam[3],gdalParam[4],gdalParam[5])
    r=ds.read(1)
    ds.close()

    polys=list()
    for pol, value in features.shapes(r, transform=affParam):
        if value>0:
            polys.append(shape(pol))
            # print("Image value:")
            # print(value)
        # print("Geometry:")
        # pprint.pprint(shape)
    if len(polys)>1:
        poly = cascaded_union(polys)
    else:
        poly=polys[0]

    return(poly)

def prepareJSON(poly,props):
    s=json.dumps(mapping(poly))
    geom=json.loads(s)

    poly_utm=wgs2utm(poly)

    feat={
        'type':'Feature',
        'properties':props,
        'geometry':geom
        }

    feat['properties']['area']=poly_utm.area
    return(feat)

def wgs2utm(geom):
    project = partial(
        pyproj.transform,
        pyproj.Proj(init='epsg:4326'),
        pyproj.Proj(init='epsg:32724'))
    geom_utm=transform(project,geom)
    return(geom_utm)

def getProperties(f):
    metalist=f.split('_')
    sentx=metalist[0]
    meta={
        # 'source_id':metalist[0],
        'ingestion_time':datetime.datetime.strptime(metalist[4],'%Y%m%dT%H%M%S'),
        'id_jrc':int(metalist[9]),}
    if sentx.startswith('S1'):
        meta['source_id']=1
    return(meta)
