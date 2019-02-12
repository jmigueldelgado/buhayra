import os
import sys
from datetime import datetime
import logging
from buhayra.getpaths import *
from buhayra.credentials import *
import subprocess

def insert_into_NEB(feat,neb):
    logger = logging.getLogger('root')
    # logger.debug('id - ' + str(feat['properties']['id_jrc']) + ' - type' + feat['geometry']['type'])
    # logger.debug("Ingestion Date:%s",feat["properties"]["ingestion_time"])
    #feat_id = neb.update_one({'properties.id_jrc':feat["properties"]["id_jrc"] , 'properties.ingestion_time' :feat["properties"]["ingestion_time"] },{'$set':feat},upsert=True).upserted_id
    #logger.debug('Inserted feature ID: %s',feat_id)
    result = neb.update_one({'properties.id_jrc':feat["properties"]["id_jrc"] , 'properties.ingestion_time' :feat["properties"]["ingestion_time"] },{'$set':feat},upsert=True)
    return(result.upserted_id)

def insert_into_postgres_NEB(src_path,o_std,o_err):
    logger = logging.getLogger('root')

    pg_login = ('PG:host='+
        postgis_host+
        ' dbname=watermasks user=' +
        postgis_user+
        ' password='+
        postgis_pass)

    call=['nohup',
        'ogr2ogr',
        '-f',
        'PostgreSQL',
        # '--config',
        # 'PG_USE_COPY YES',
        pg_login,
        src_path,
        '-nln',
        'neb',
        '-append',
        '-skipfailures']

    r = subprocess.Popen(call,
        stdout=o_std,
        stderr=o_err,
        preexec_fn=os.setpgrp)

def write_poly_loop():
    logger = logging.getLogger('root')
    wm=fiona.open(home['home']+'/proj/buhayra/buhayra/auxdata/wm_utm_simplf.gpkg','r')
    while(selectTiff(polOut)):
        f=selectTiff(polOut)
        logger.debug('Selecting tif %s',f)
        poly=tif2shapely(f)
        feat=prepareJSON(poly,f)
        feat=select_intersecting_polys(feat,wm)
        feat['properties']['ingestion_time']=None
        with open(home['home']+'/'+f[:-3]+'geojson', 'w') as fjson:
            json.dump(feat, fjson)
            os.remove(polOut + '/' + f)
            os.remove(polOut+'/'+f[:-3]+'json')


def select_tiffs_year_month(Y,M):
    logger = logging.getLogger('root')
    if(len(listdir(polOut))<1):
        logger.info(polOut+" is empty! Nothing to do. Exiting and returning None.")
        tiffs_in_ym=None
    else:
        timestamp=list()
        tiffs_in_ym=list()
        for tif in listdir(polOut):
            if not tif.startswith('S'):
                continue
            stamp=datetime.datetime.strptime(tif.split('_')[4],'%Y%m%dT%H%M%S')
            if re.search('.tif$',tif) and stamp.year==Y and stamp.month==M:
                tiffs_in_ym.append(tif)
                timestamp.append(stamp)
        if(len(timestamp)<1):
            logger.info(polOut+" has no tiffs for year "+str(Y)+" and month "+str(M)+"Exiting and returning None.")
            tiffs_in_ym=None
    return(tiffs_in_ym)





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
