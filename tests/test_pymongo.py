from pymongo import MongoClient
from bson import json_util
import geojson
import json
import os
import sys
import socket
from datetime import datetime
# from sshtunnel import SSHTunnelForwarder
from buhayra.defAggregations import *
from buhayra.getpaths import *
import logging
import subprocess as sp

from shapely.geometry import shape

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
    neb = db.neb ##  collection

    # db.drop_collection('neb')

    poly = neb.find_one()
    shape(poly['geometry'])
