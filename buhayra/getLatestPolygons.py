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
        logger.info("connecting to remote mongodb")       
        client = MongoClient('mongodb://'+ MONGO_USER + ':' + MONGO_PASS + '@' + MONGO_HOST + '/' + MONGO_DB) #### untested!
    else:
        logger.info("connecting to local host")
        try:
            client = MongoClient('mongodb://'+ MONGO_USER + ':' + MONGO_PASS + '@' + MONGO_HOST + '/' + MONGO_DB)
        except:
            logger.exception("Error: something went wrong when connecting to mongodb on host " + MONGO_HOST)
            raise

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
