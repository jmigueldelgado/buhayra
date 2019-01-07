from pymongo import MongoClient
import os
import sys
from datetime import datetime
import logging
from buhayra.polygonize import *
from buhayra.getpaths import *
from buhayra.credentials import *
# import dask
# from dask.distributed import Client, progress, LocalCluster


# f=select_tiffs_year_month(2018,4)[0]
# wm=fiona.open(home['home']+'/proj/buhayra/buhayra/auxdata/wm_utm_simplf.gpkg','r')

def insert_loop(tiffs):
    logger = logging.getLogger('root')
    # cluster = LocalCluster(processes=False,n_workers=1,threads_per_worker=2)
    # client = Client(cluster)

    # load_watermask=dask.delayed(load_watermask)
    # load_metadata=dask.delayed(load_metadata)
    # raster2shapely=dask.delayed(raster2shapely)
    # prepareJSON=dask.delayed(prepareJSON)
    # select_intersecting_polys=dask.delayed(select_intersecting_polys)
    # insert_into_NEB=dask.delayed(insert_into_NEB)
    # remove_watermask=dask.delayed(remove_watermask)

    logger = logging.getLogger('root')
    neb = connect_to_NEB()
    out=list()
    with fiona.open(home['home']+'/proj/buhayra/buhayra/auxdata/wm_utm_simplf.gpkg','r') as wm:
        for f in tiffs:
            r = load_watermask(f)
            metadata = load_metadata(f)
            poly = raster2shapely(r,metadata)
            feat = prepareJSON(poly,f,metadata)
            feat_wm = select_intersecting_polys(feat,wm)
            feat_id = insert_into_NEB(feat_wm,neb)
            out.append(feat_id)
            rm = remove_watermask(f,feat_id)
            out.append(rm)

    # total=dask.delayed(out)
    # total.compute()

def connect_to_NEB():
    logger = logging.getLogger('root')

    # client = MongoClient('127.0.0.1', server.local_bind_port) # server.local_bind_port is assigned local port
    client = MongoClient('mongodb://'+ MONGO_USER + ':' + MONGO_PASS + '@' + MONGO_HOST + '/' + MONGO_DB)
    logger.info("%s",client)
    db = client.sar2watermask
    neb = db.neb ##  collection
    logger.info("Connected to mongodb:")
    logger.info("%s",neb)

    return neb


def insert_into_NEB(feat,neb):
    logger = logging.getLogger('root')
    # logger.debug('id - ' + str(feat['properties']['id_jrc']) + ' - type' + feat['geometry']['type'])
    # logger.debug("Ingestion Date:%s",feat["properties"]["ingestion_time"])
    #feat_id = neb.update_one({'properties.id_jrc':feat["properties"]["id_jrc"] , 'properties.ingestion_time' :feat["properties"]["ingestion_time"] },{'$set':feat},upsert=True).upserted_id
    #logger.debug('Inserted feature ID: %s',feat_id)
    if feat is not None:
        result = neb.update_one({'properties.id_jrc':feat["properties"]["id_jrc"] , 'properties.ingestion_time' :feat["properties"]["ingestion_time"] },{'$set':feat},upsert=True)
        id=result.upserted_id
    # result = neb.insert_one(feat)
    else:
        id=None
    return(id)


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
