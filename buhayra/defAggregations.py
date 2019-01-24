from pymongo import MongoClient
import json
import geojson
from bson import json_util
import os
import sys
import datetime
from buhayra.getpaths import *
import socket
import subprocess

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




## also for manual use
def getLatestIngestionTime(s2w):
    pipeline = [
        { "$sort" : {"properties.id_jrc" : 1, "properties.ingestion_time" : 1 }},
        {
            "$group":
            {
                "_id" : "$properties.id_jrc",
                "latestIngestion" : {
                    "$last":"$properties.ingestion_time"
                }
            }
        }
    ]

    aggrLatest=list(s2w.aggregate(pipeline=pipeline))
    latest=list()

    for feat in aggrLatest:
        poly = s2w.find({'properties.id_jrc' : feat['_id'],'properties.ingestion_time':feat['latestIngestion']},{'properties.id_jrc' : 1,'properties.ingestion_time' : 1})
        latest.append(poly[0])
    return(latest)


def getLatestPolysMinusX(s2w,x):
    thresh_date=datetime.datetime.now() - datetime.timedelta(days=x*30)
    pipeline = [
        { "$match" : {"properties.ingestion_time" : {"$lte" : thresh_date}}},
        { "$sort" : {"properties.id_jrc" : 1, "properties.ingestion_time" : 1 }},
        {
            "$group":
            {
                "_id" : "$properties.id_jrc",
                "latestIngestion" : {
                    "$last":"$properties.ingestion_time"
                }
            }
        }
    ]

    aggrLatest=list(s2w.aggregate(pipeline=pipeline,allowDiskUse=True))

    latest=list()

    for feat in aggrLatest:
        poly = s2w.find({'properties.id_jrc' : feat['_id'],'properties.ingestion_time':feat['latestIngestion']})
        latest.append(poly[0])
    return(latest)



def getTimeSeries(s2w):
    pipeline = [
        {
            "$group":
            {
                "_id" : "$properties.id_jrc",
                "timeSeries" : { "$push" : { "time" : "$properties.ingestion_time" , "area" : "$properties.area"} }
            }

        }
    ]

    TimeSeries = list(s2w.aggregate(pipeline=pipeline))
    return(TimeSeries)


#dict={'key1':{'subkey1':'one','subkey2':'two'},'key2':2}
#'subkey1' in dict['key1']

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
