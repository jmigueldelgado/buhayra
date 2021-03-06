import json
import geojson
from bson import json_util
import os
import sys
import datetime
from buhayra.getpaths import *
import socket
import subprocess

def getRandomSubset():

    bbox = Polygon([[-40.20,-3.0], [-38.3,-3.0], [-38.3,-4.50], [-40.20,-4.50]])
    path_to_geojson = aggr.ogr_getJRC()
    with fiona.open(path_to_geojson,'r') as latest:
        ids=list()

        for feat in latest:
            if not shape(feat['geometry']).within(bbox):
                continue
            ids.append('{}'.format(feat['properties']['id_jrc']))

    path_to_geojson = aggr.ogr_getRandomSubset(ids)


def ogr_getJRC():
    path_to_geojson = os.path.join(home['home'],'JRC.geojson')
    if os.path.isfile(path_to_geojson):
        pass
    else:
        with open(os.path.join(home['home'],'ogr_query.log'), 'a') as o_std, open(os.path.join(home['home'], 'ogr_query.err'), 'a') as o_err:
            #query = 'geom from (select distinct on (id_jrc) id_jrc, ingestion_time, area, geom, id from neb order by id_jrc, ingestion_time desc) as subquery using unique id using srid=4326'
            query = 'select distinct on (id_jrc) * from jrc_neb order by id_jrc desc'
            call=['nohup','ogr2ogr','-f','GeoJSON' ,path_to_geojson, 'PG:host='+postgis_host+' dbname=watermasks user=' +postgis_user+' password='+postgis_pass,'-sql',query]
            p = subprocess.Popen(call, stdout=o_std, stderr=o_err, preexec_fn=os.setpgrp)
            while p.wait()!=0:
                pass
    return path_to_geojson

def ogr_getLatestIngestionTime():
    path_to_geojson = os.path.join(home['home'],'latest-watermask'+ datetime.datetime.today().strftime('%Y-%m-%d')+'.geojson')
    if os.path.isfile(path_to_geojson):
        pass
    else:
        with open(os.path.join(home['home'],'ogr_query.log'), 'a') as o_std, open(os.path.join(home['home'], 'ogr_query.err'), 'a') as o_err:
            #query = 'geom from (select distinct on (id_jrc) id_jrc, ingestion_time, area, geom, id from neb order by id_jrc, ingestion_time desc) as subquery using unique id using srid=4326'
            query = 'select distinct on (id_jrc) id_jrc, ingestion_time, area, ST_centroid(geom), id from neb order by id_jrc, ingestion_time desc'
            call=['nohup','ogr2ogr','-f','GeoJSON' ,path_to_geojson, 'PG:host='+postgis_host+' dbname=watermasks user=' +postgis_user+' password='+postgis_pass,'-sql',query]
            p = subprocess.Popen(call, stdout=o_std, stderr=o_err, preexec_fn=os.setpgrp)
            while p.wait()!=0:
                pass

    return path_to_geojson


def ogr_getTimeSeriesID(id):
    path_to_geojson = os.path.join(home['home'],'time-series-'+ str(id) +'.geojson')
    with open(os.path.join(home['home'],'ogr_query.log'), 'a') as o_std, open(os.path.join(home['home'], 'ogr_query.err'), 'a') as o_err:
        #query = 'geom from (select distinct on (id_jrc) id_jrc, ingestion_time, area, geom, id from neb order by id_jrc, ingestion_time desc) as subquery using unique id using srid=4326'
        query = ('select id_jrc, ingestion_time, area, geom' +
            ' from neb'+
            ' order by id_jrc, ingestion_time desc')
        call=['nohup','ogr2ogr','-f','GeoJSON' ,path_to_geojson, 'PG:host='+postgis_host+' dbname=watermasks user=' +postgis_user+' password='+postgis_pass,'-sql',query]
        p = subprocess.Popen(call, stdout=o_std, stderr=o_err, preexec_fn=os.setpgrp)
        while p.wait()!=0:
            pass

    return path_to_geojson

def ogr_getRandomSubset(idlist):
    path_to_geojson = os.path.join(home['home'],'time-series-'+ datetime.datetime.today().strftime('%Y-%m-%d') +'.geojson')
    with open(os.path.join(home['home'],'ogr_query.log'), 'a') as o_std, open(os.path.join(home['home'], 'ogr_query.err'), 'a') as o_err:
        #query = 'geom from (select distinct on (id_jrc) id_jrc, ingestion_time, area, geom, id from neb order by id_jrc, ingestion_time desc) as subquery using unique id using srid=4326'
        query = ('select neb.id_jrc, neb.ingestion_time, neb.area, neb.wmxjrc_area, neb.geom'+
                 ' from neb'+
                 ' where neb.id_jrc in ('+','.join(idlist)+')' +
                 ' order by id_jrc, ingestion_time desc')
        call=['nohup','ogr2ogr','-f','GeoJSON' ,path_to_geojson, 'PG:host='+postgis_host+' dbname=watermasks user=' +postgis_user+' password='+postgis_pass,'-sql',query]
        p = subprocess.Popen(call, stdout=o_std, stderr=o_err, preexec_fn=os.setpgrp)
        while p.wait()!=0:
            pass
    return path_to_geojson

def ogr_getAll():
    path_to_geojson = os.path.join(home['home'],'time-series-'+ datetime.datetime.today().strftime('%Y-%m-%d') +'.geojson')
    with open(os.path.join(home['home'],'ogr_query.log'), 'a') as o_std, open(os.path.join(home['home'], 'ogr_query.err'), 'a') as o_err:
        #query = 'geom from (select distinct on (id_jrc) id_jrc, ingestion_time, area, geom, id from neb order by id_jrc, ingestion_time desc) as subquery using unique id using srid=4326'
        query = ('select neb.id_jrc, neb.ingestion_time, neb.area, neb.wmxjrc_area, neb.geom'+
                 ' from neb'+
                 ' order by id_jrc, ingestion_time desc')
        call=['nohup','ogr2ogr','-f','GeoJSON' ,path_to_geojson, 'PG:host='+postgis_host+' dbname=watermasks user=' +postgis_user+' password='+postgis_pass,'-sql',query]
        p = subprocess.Popen(call, stdout=o_std, stderr=o_err, preexec_fn=os.setpgrp)
        while p.wait()!=0:
            pass
    return path_to_geojson

def aggr2geojson(polys):
    feats=[]
    for poly in polys:
        oid=json.loads(json.dumps(poly['_id'],default=json_util.default))
        dttm=poly['properties']['ingestion_time']
        dttmstr=dttm.strftime("%Y-%m-%d %H:%M:%S")
        poly['properties']['ingestion_time']=dttmstr
        del poly['_id']
        poly['properties']['oid']=oid['$oid']

        ### rename to insert into postgis
        if 'platformname' in poly['properties']:
            poly['properties']['source_id'] = poly['properties'].pop('platformname')
            if poly['properties']['source_id']=='Sentinel-1':
                poly['properties']['source_id']=1
            elif poly['properties']['source_id']=='Sentinel-2':
                poly['properties']['source_id']=2
        elif 'source_id' in poly['properties']:
            print('dealing with correct geojson attributes, no need to change anything\n')
        else:
            print('probably one of the first scenes to be processed, before adding sentinel-2, so it must be sentinel-1! passing 1 as source_id.\n')
            poly['properties']['source_id']=1

        if poly['geometry'] is None:
            feats.append(geojson.Feature(geometry=None,properties=poly['properties']))
        else:
            ## mixing poly and multiply is not accepted by postgis. we will force Polygon into MultiPolygon
            if len(poly['geometry']['coordinates'])>0:
                mp=geojson.MultiPolygon()

            ## now we have to correct syntax of MultiPolygon which was forced from Polygon so it generates valid geojson in the end
            if poly["geometry"]["type"]=='Polygon':
                poly["geometry"]["coordinates"]=[poly["geometry"]["coordinates"]]
            #if len(poly['geometry']['coordinates'])==1:
            #    mp=geojson.Polygon()

            mp['coordinates']=poly['geometry']['coordinates']

            feats.append(geojson.Feature(geometry=mp,properties=poly['properties']))

    feat_col=geojson.FeatureCollection(feats)
    return(feat_col)
