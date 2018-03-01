from pymongo import MongoClient
import json
import os
import sys
from datetime import datetime
from sshtunnel import SSHTunnelForwarder

from modules.getPaths import *

server = SSHTunnelForwarder(
    MONGO_HOST,
    ssh_username=MONGO_USER,
    ssh_password=MONGO_PASS,
    remote_bind_address=('127.0.0.1', MONGO_PORT))

server.start()

client = MongoClient('127.0.0.1', server.local_bind_port) # server.local_bind_port is assigned local port

## in case you want the local host:
#client = MongoClient('mongodb://localhost:27017/')

db = client.sar2watermask
s2w = db.sar2watermask ##  collection

#print(db.collection_names())

newlist = []
items=os.listdir(polOut)

for names in items:
    if names.endswith('simplified.geojson'):
        newlist.append(names)

for in_file in newlist:
    print('\n inserting ' + in_file + ' in mongodb\n')

    with open(polOut + '/' + in_file) as f:
        data = json.load(f)

    for feat in data["features"]:
        dttm = datetime.strptime(feat["properties"]["ingestion_time"],"%Y/%m/%d %H:%M:%S+00")
        feat["properties"]["ingestion_time"] = dttm
        #dicio = {"geometry":feat["geometry"],"id_cogerh":feat["properties"]["id_cogerh"]}
        feat_id = s2w.update_one(feat,{"$set" : feat},upsert=True).upserted_id
#        feat_id = s2w.insert_one(feat).inserted_id
        print feat_id

    print('\n removing ' + in_file + '\n')
    os.remove(polOut + '/' + in_file)

#### IT WORKS!!!

server.stop()

#### This works, but would need python installed on the webserver and mount of orson's /mnt/scratch, which is not very reliable

#ssh = paramiko.SSHClient()
#ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#ssh.connect(hostname=MONGO_HOST,username=MONGO_USER,password=MONGO_PASS)
#stdin, stdout, stderr = ssh.exec_command('python ')
#ssh.close()
