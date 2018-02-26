from pymongo import MongoClient
from bson import json_util
import geojson
import json
import os
import sys
from datetime import datetime
from sshtunnel import SSHTunnelForwarder
from defAggregations import *
from getPaths import *
import subprocess as sp

if home['home']!='/home/riemer':
    server = SSHTunnelForwarder(
        MONGO_HOST,
        ssh_username=MONGO_USER,
        ssh_password=MONGO_PASS,
        remote_bind_address=('127.0.0.1', MONGO_PORT))

    server.start()
    print("started ssh tunnel")

    client = MongoClient('127.0.0.1', server.local_bind_port) # server.local_bind_port is assigned local port
else:
    print("connecting to local host")
    client = MongoClient('mongodb://localhost:27017/')


db = client.sar2watermask
s2w = db.sar2watermask ##  collection

#TimeSeries = getTimeSeries(s2w)
latestIngestionTime = getLatestIngestionTime(s2w)

## get most recent polygons from mongodb
polys = getLatestPolys(s2w)
polys1 = getLatestPolysMinusX(s2w,1)
polys2 = getLatestPolysMinusX(s2w,2)
polys3 = getLatestPolysMinusX(s2w,3)

## get geojson standard feature collection
feat_col=aggr2geojson(polys)
feat_col1=aggr2geojson(polys1)
feat_col2=aggr2geojson(polys2)
feat_col3=aggr2geojson(polys3)

## write
f=open(home['home']+'/0_latest.geojson','w')
geojson.dump(feat_col,f)
f.close()

f=open(home['home']+'/1_month_ago.geojson','w')
geojson.dump(feat_col1,f)
f.close()

f=open(home['home']+'/2_months_ago.geojson','w')
geojson.dump(feat_col2,f)
f.close()

f=open(home['home']+'/3_months_ago.geojson','w')
geojson.dump(feat_col3,f)
f.close()

# merge all geojson to geopackage
f0 = home['home']+'/watermaskVis/0_latest.geojson'
f1 = home['home']+'/watermaskVis/1_month_ago.geojson'
f2 = home['home']+'/watermaskVis/2_month_ago.geojson'
f3 = home['home']+'/watermaskVis/3_month_ago.geojson'

### moved to crontab as bash script
#cmd = ['ogrmerge.py', '-single','-f', 'GPKG', '-o', 'last4month.gpkg', f0, f1, f2, f3]
#sp.call(cmd)

if home['home']!='/home/riemer':
    server.stop()
