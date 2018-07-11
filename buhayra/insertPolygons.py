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
    logging.basicConfig(filename=home['home'] + "/5_insert_polys.pylog",level=logging.DEBUG)

    server = SSHTunnelForwarder(
        MONGO_HOST,
        ssh_username=MONGO_USER,
        ssh_password=MONGO_PASS,
        remote_bind_address=('127.0.0.1', MONGO_PORT))

    server.start()

    logging.info("%s",server)

    client = MongoClient('127.0.0.1', server.local_bind_port) # server.local_bind_port is assigned local port

    ## in case you want the local host:
    #client = MongoClient('mongodb://localhost:27017/')

    db = client.sar2watermask
    s2w = db.sar2watermask ##  collection
    #print(db.collection_names())
    logging.info("Connected to mongodb")
    logging.info("db.collection_names()")
    logging.info("%s",db.collection_names())

    newlist = []
    items=os.listdir(polOut)
    for names in items:
        if names.endswith('simplified.geojson'):
            newlist.append(names)

    for in_file in newlist:
        logging.info('\n inserting ' + in_file + ' in mongodb\n')

        with open(polOut + '/' + in_file) as f:
            data = geojson.load(f)

        for feat in data["features"]:
            dttm = datetime.strptime(feat["properties"]["ingestion_time"],"%Y/%m/%d %H:%M:%S+00")
            feat["properties"]["ingestion_time"] = dttm
            feat["properties"]["source_id"] = int(feat["properties"]["source_id"])

            logging.info("Current feature's properties:")
            logging.info("Ingestion Date:%s",feat["properties"]["ingestion_time"])
            logging.info("ID:%s",feat["properties"]["id_cogerh"])

            #dicio = {"geometry":feat["geometry"],"id_cogerh":feat["properties"]["id_cogerh"]}
            feat_id = s2w.update_one(feat,upsert=True).upserted_id
            #feat_id = s2w.insert_one(feat).inserted_id
            logging.info('Inserted feature ID: %s',feat_id)
        logging.info('\n\n\n moving away ' + in_file + '\n\n\n')
        shutil.move(polOut + '/' + in_file,procOut)

    #### IT WORKS!!!

    server.stop()

#### This works, but would need python installed on the webserver and mount of orson's /mnt/scratch, which is not very reliable

#ssh = paramiko.SSHClient()
#ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#ssh.connect(hostname=MONGO_HOST,username=MONGO_USER,password=MONGO_PASS)
#stdin, stdout, stderr = ssh.exec_command('python ')
#ssh.close()
