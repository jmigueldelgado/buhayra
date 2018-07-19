from pymongo import MongoClient
import geojson
import os
import sys
from datetime import datetime
from sshtunnel import SSHTunnelForwarder
import logging
import shutil

from buhayra.getpaths import *

def insertPolygons():
    logger = logging.getLogger(__name__)

    ### SSHTunnelForwarder no longer necessary with remote access to mongodb enabled. See:
#   https://ianlondon.github.io/blog/mongodb-auth/
#   and
#   allow port 27017 in firewall with ufw


#    client = MongoClient('127.0.0.1', server.local_bind_port) # server.local_bind_port is assigned local port
    client = MongoClient('mongodb://'+ MONGO_USER + ':' + MONGO_PASS + '@' + MONGO_HOST + '/' + MONGO_DB)
    logger.info("%s",client)

    ## in case you want the local host:
    #client = MongoClient('mongodb://localhost:27017/')

    db = client.sar2watermask
    s2w = db.sar2watermask ##  collection
    #print(db.collection_names())
    logger.info("Connected to mongodb:")
    logger.info("%s",s2w)

    newlist = []
    items=os.listdir(polOut)
    for names in items:
        if names.endswith('simplified.geojson'):
            newlist.append(names)

    for in_file in newlist:
        logger.info('\n inserting ' + in_file + ' in mongodb\n')

        with open(polOut + '/' + in_file) as f:
            data = geojson.load(f)

        for feat in data["features"]:
            dttm = datetime.strptime(feat["properties"]["ingestion_time"],"%Y/%m/%d %H:%M:%S+00")
            feat["properties"]["ingestion_time"] = dttm
            feat["properties"]["source_id"] = int(feat["properties"]["source_id"])

            logger.info("Current feature's properties:")
            logger.info("Ingestion Date:%s",feat["properties"]["ingestion_time"])
            logger.info("ID:%s",feat["properties"]["id_funceme"])
            feat_id = s2w.update_one({'properties.id_funceme':feat["properties"]["id_funceme"] , 'properties.ingestion_time' :feat["properties"]["ingestion_time"] },feat,upsert=True).upserted_id
            logger.info('Inserted feature ID: %s',feat_id)
        logger.info('\n\n\n moving away ' + in_file + '\n\n\n')
        shutil.move(polOut + '/' + in_file,procOut)

#    server.stop()
