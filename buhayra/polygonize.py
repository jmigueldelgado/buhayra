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
from numpy import amax
from buhayra.thresholding import *


def tif2shapely(f):
    with rasterio.open(polOut+'/'+f,'r') as ds:
        # ds.profile.update(dtype=rasterio.int32)
        # with open(polOut+'/'+f[:-3]+'json', 'r') as fjson:
        #     gdalParam = json.load(fjson)
        # affParam=rasterio.Affine.from_gdal(gdalParam[0],gdalParam[1],gdalParam[2],gdalParam[3],gdalParam[4],gdalParam[5])
        r=ds.read(1)
        # ds.close()
        if amax(r)==0:
            poly = Polygon()
        else:
            polys=list()
            for pol, value in features.shapes(r, transform=ds.transform):
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

def getProperties(f):
    # with open(polOut+'/'+f[:-3]+'json', 'r') as fjson:
    #     param = json.load(fjson)

    metalist=f[:-4].split('_')
    sentx=metalist[0]
    meta={
        # 'source_id':metalist[0],
        'ingestion_time':datetime.datetime.strptime(metalist[4],'%Y%m%dT%H%M%S'),
        'id_jrc':int(metalist[9]),}
        # 'threshold':int(param[6]),}
    if sentx.startswith('S1'):
        meta['source_id']=1
    else:
        meta['source_id']=None
    return(meta)

def prepareJSON(poly,f):
    props=getProperties(f)
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

def write_pol(pols,f):
    meta=getProperties(f)

    schema = {
        'geometry': str(pols.geom_type),
        'properties': {'id': 'int'}#,'threshold':'int'},
    }
    fpath=home['home']+'/'+f[:-3]+'gpkg'

    if not os.path.isfile(fpath):
        with fiona.open(fpath, 'w',
                        layer=str(pols.geom_type),
                        driver='GPKG',
                        schema=schema) as dst:
            dst.write({
                'geometry':mapping(pols),
                'properties': {'id':meta['id_jrc']}#,'threshold':meta['threshold']}
            })


def select_intersecting_polys(feat,wm):

    geom=geojson2shapely(feat['geometry'])
    geom=checknclean(geom)

    project = partial(
        pyproj.transform,
        pyproj.Proj(init='epsg:32724'),
        pyproj.Proj(init='epsg:4326'))

    for wm_feat in wm:
        if int(wm_feat['id'])==feat['properties']['id_jrc']:
            refgeom=geojson2shapely(wm_feat['geometry'])
            refgeom=checknclean(refgeom)
            refgeom=transform(project,refgeom)
            break

    inters=list()
    if len(geom)>1:
        for poly in geom:
            if poly.intersects(refgeom):
                inters.append(poly)
        if len(inters)>1:
            inters = cascaded_union(inters)
        else:
            inters=inters[0]
        s=json.dumps(mapping(inters))
    else:
        if geom.intersects(refgeom):
            s=json.dumps(mapping(geom))

    feat['geometry']=json.loads(s)
    return(feat)
