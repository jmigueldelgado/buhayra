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
import logging
import subprocess as sp

def connect_and_get(x):
    logger = logging.getLogger('root')
    if socket.gethostname()!='ubuntuserver':
        server = SSHTunnelForwarder(
            MONGO_HOST,
            ssh_username=MONGO_USER,
            ssh_password=MONGO_PASS,
            remote_bind_address=('127.0.0.1', MONGO_PORT))

        server.start()
        logger.info("started ssh tunnel")

        client = MongoClient('127.0.0.1', server.local_bind_port) # server.local_bind_port is assigned local port
    else:
        logger.info("connecting to local host")
        client = MongoClient('mongodb://localhost:27017/')


    db = client.sar2watermask
    s2w = db.sar2watermask ##  collection

    #TimeSeries = getTimeSeries(s2w)
    #latestIngestionTime = getLatestIngestionTime(s2w)

    ## get polygons from x months ago from mongodb
    polys = getLatestPolysMinusX(s2w,x)
    ## get geojson standard feature collection
    feat_col=aggr2geojson(polys)

    logger.info('writing out to ' + home['home']+'/load_to_postgis/latest.geojson')
    f=open(home['home']+'/load_to_postgis/latest.geojson','w')
    geojson.dump(feat_col,f)
    f.close()

    if socket.gethostname()!='ubuntuserver':
        server.stop()
