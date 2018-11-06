from pymongo import MongoClient
import os
import sys
from datetime import datetime
import logging
from buhayra.polygonize import *
from buhayra.getpaths import *
from buhayra.credentials import *



def insertLoop():
    while (len(listdir(polOut))>1):
        f=selectTiff(polOut)
        poly=tif2shapely(f)
        props=getProperties(f)
        feat=prepareJSON(poly,props)
        feat_id=insertNEB(feat)
        logger.debug('Inserted feature ID: %s',feat_id)





def insertNEB(feat):
    logger = logging.getLogger('root')

    logger.info("logger start")
    # client = MongoClient('127.0.0.1', server.local_bind_port) # server.local_bind_port is assigned local port
    client = MongoClient('mongodb://'+ MONGO_USER + ':' + MONGO_PASS + '@' + MONGO_HOST + '/' + MONGO_DB)
    logger.info("%s",client)
    ## in case you want the local host:
    #client = MongoClient('mongodb://localhost:27017/')

    db = client.neb
    neb = db.neb ##  collection
    # print(db.collection_names())
    logger.info("Connected to mongodb:")
    logger.info("%s",s2w)
    logger.debug('id - ' + str(feat['properties']['id_jrc']) + ' - type' + feat['geometry']['type'])
    logger.debug("Ingestion Date:%s",feat["properties"]["ingestion_time"])
    #feat_id = neb.update_one({'properties.id_jrc':feat["properties"]["id_jrc"] , 'properties.ingestion_time' :feat["properties"]["ingestion_time"] },{'$set':feat},upsert=True).upserted_id
    #logger.debug('Inserted feature ID: %s',feat_id)

    feat_id = neb.insert(feat).inserted_id
    logger.info('moving away ' + f)
    os.rename(polOut + '/' + f,procOut + '/' + f)
    return(feat_id)

def insertPolygons():
    logger = logging.getLogger('root')

    ### SSHTunnelForwarder no longer necessary with remote access to mongodb enabled. See:
#   https://ianlondon.github.io/blog/mongodb-auth/
#   and
#   allow port 27017 in firewall with ufw

    logger.info("logger start")
    # client = MongoClient('127.0.0.1', server.local_bind_port) # server.local_bind_port is assigned local port
    client = MongoClient('mongodb://'+ MONGO_USER + ':' + MONGO_PASS + '@' + MONGO_HOST + '/' + MONGO_DB)
    logger.info("%s",client)
    ## in case you want the local host:
    #client = MongoClient('mongodb://localhost:27017/')

    db = client.sar2watermask
    s2w = db.sar2watermask ##  collection
    # print(db.collection_names())
    logger.info("Connected to mongodb:")
    logger.info("%s",s2w)

    newlist = []
    items=os.listdir(polOut)
    for names in items:
        if names.endswith('simplified.geojson'):
            newlist.append(names)

    for in_file in newlist:
        logger.info('inserting ' + in_file + ' in mongodb')

        with open(polOut + '/' + in_file) as f:
            data = geojson.load(f)

        count=0
        countNone=0
        for feat in data["features"]:
            logger.debug('id - ' + str(feat['properties']['id_funceme']) + ' - type' + feat['geometry']['type'])
            dttm = datetime.strptime(feat["properties"]["ingestion_time"],"%Y/%m/%d %H:%M:%S+00")
            feat["properties"]["ingestion_time"] = dttm
            feat["properties"]["source_id"] = int(feat["properties"]["source_id"])
            logger.debug("Ingestion Date:%s",feat["properties"]["ingestion_time"])
            feat_id = s2w.update_one({'properties.id_funceme':feat["properties"]["id_funceme"] , 'properties.ingestion_time' :feat["properties"]["ingestion_time"] },{'$set':feat},upsert=True).upserted_id
            logger.debug('Inserted feature ID: %s',feat_id)
            if feat_id != None:
                count = count + 1
            if feat_id == None:
                countNone = countNone + 1
        logger.info('inserted %d features',count)
        logger.info('there were %d Nones',countNone)
        logger.info('moving away ' + in_file)
        shutil.move(polOut + '/' + in_file,procOut + '/' + in_file)

#    server.stop()



def testMongoConnect():
    logger = logging.getLogger('root')

    ### SSHTunnelForwarder no longer necessary with remote access to mongodb enabled. See:
#   https://ianlondon.github.io/blog/mongodb-auth/
#   and
#   allow port 27017 in firewall with ufw

    logger.info("logger start")
    # client = MongoClient('127.0.0.1', server.local_bind_port) # server.local_bind_port is assigned local port
    client = MongoClient('mongodb://'+ MONGO_USER + ':' + MONGO_PASS + '@' + MONGO_HOST + '/' + MONGO_DB)
    logger.info("%s",client)
    ## in case you want the local host:
    #client = MongoClient('mongodb://localhost:27017/')

    db = client.sar2watermask
    s2w = db.sar2watermask ##  collection
    logger.debug(db.collection_names())
    print(db.collection_names())
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
            logger.debug('id - ' + str(feat['properties']['id_funceme']) + ' - type' + feat['geometry']['type'])
            dttm = datetime.strptime(feat["properties"]["ingestion_time"],"%Y/%m/%d %H:%M:%S+00")
            feat["properties"]["ingestion_time"] = dttm
            feat["properties"]["source_id"] = int(feat["properties"]["source_id"])
            logger.debug("Ingestion Date:%s",feat["properties"]["ingestion_time"])
            feat_id = s2w.update_one({'properties.id_funceme':feat["properties"]["id_funceme"] , 'properties.ingestion_time' :feat["properties"]["ingestion_time"] },{'$set':feat},upsert=True).upserted_id
            logger.debug('Inserted feature ID: %s',feat_id)
            if feat_id != None:
                break
        if feat_id != None:
            logger.info('id - ' + str(feat['properties']['id_funceme']) + ' - type' + feat['geometry']['type'])
            logger.info("Ingestion Date:%s",feat["properties"]["ingestion_time"])
            logger.info('Inserted feature ID: %s',feat_id)
            break
