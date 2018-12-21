from pymongo import MongoClient
import json
import geojson
from bson import json_util
import os
import sys
from datetime import datetime,timedelta
from buhayra.getpaths import *
import socket
# from sshtunnel import SSHTunnelForwarder



## also for manual use
def getLatestIngestionTime(s2w):
    pipeline = [
        { "$sort" : {"properties.id_funceme" : 1, "properties.ingestion_time" : 1 }},
        {
            "$group":
            {
                "_id" : "$properties.id_funceme",
                "latestIngestion" : {
                    "$last":"$properties.ingestion_time"
                }
            }
        }
    ]

    aggrLatest=list(s2w.aggregate(pipeline=pipeline))
    latest=list()

    for feat in aggrLatest:
        poly = s2w.find({'properties.id_funceme' : feat['_id'],'properties.ingestion_time':feat['latestIngestion']},{'properties.id_funceme' : 1,'properties.ingestion_time' : 1})
        latest.append(poly[0])
    return(latest)


def getLatestPolysMinusX(s2w,x):
    thresh_date=datetime.now() - timedelta(days=x*30)
    pipeline = [
        { "$match" : {"properties.ingestion_time" : {"$lte" : thresh_date}}},
        { "$sort" : {"properties.id_funceme" : 1, "properties.ingestion_time" : 1 }},
        {
            "$group":
            {
                "_id" : "$properties.id_funceme",
                "latestIngestion" : {
                    "$last":"$properties.ingestion_time"
                }
            }
        }
    ]

    aggrLatest=list(s2w.aggregate(pipeline=pipeline,allowDiskUse=True))

    latest=list()

    for feat in aggrLatest:
        poly = s2w.find({'properties.id_funceme' : feat['_id'],'properties.ingestion_time':feat['latestIngestion']})
        latest.append(poly[0])
    return(latest)



def getTimeSeries(s2w):
    pipeline = [
        {
            "$group":
            {
                "_id" : "$properties.id_funceme",
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

        ## mixing poly and multiply is not accepted by postgis. we will force Polygon into MultiPolygon
        if len(poly['geometry']['coordinates'])>0:
            mp=geojson.MultiPolygon()

        ## now we have to correct syntax of MultiPolygon which was forced from Polygon so it generates valid geojson in the end
        if poly["geometry"]["type"]=='Polygon':
            poly["geometry"]["coordinates"]=[poly["geometry"]["coordinates"]]
        #if len(poly['geometry']['coordinates'])==1:
        #    mp=geojson.Polygon()

        mp['coordinates']=poly['geometry']['coordinates']
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

        feats.append(geojson.Feature(geometry=mp,properties=poly['properties']))

    feat_col=geojson.FeatureCollection(feats)
    return(feat_col)
