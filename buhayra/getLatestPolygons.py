from pymongo import MongoClient
from bson import json_util
import geojson
import json
import os
import sys
import socket
from datetime import datetime
from sshtunnel import SSHTunnelForwarder
from buhayra.defAggregations import *
from buhayra.getpaths import *
import subprocess as sp

def connect_and_get():
    if socket.gethostname()!='ubuntuserver':
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

    ## get geojson standard feature collection
    feat_col=aggr2geojson(polys)

    ## write
    f=open(home['home']+'/load_to_postgis/latest.geojson','w')
    geojson.dump(feat_col,f)
    f.close()

    if home['hostname']!='ubuntuserver':
        server.stop()
