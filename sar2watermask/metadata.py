import psycopg2
from buhayra.getpaths import *
from buhayra.credentials import *
import buhayra.utils as utils
import os
import zipfile
import xmltodict
from datetime import datetime
import re
import logging
# ingestion_time = datetime.datetime.strptime('20181007T081706','%Y%m%dT%H%M%S')
# scene=utils.select_scene_ingestion_time(ingestion_time,sarIn)[0]

def insert_into_postgres(scenes):
    logger = logging.getLogger('root')
    logger.info("Connect to postgres with psycopg2")

    conn = psycopg2.connect(host=postgis_host,dbname='watermasks',user=postgis_user,password=postgis_pass)
    cur = conn.cursor()
    INSERT = """INSERT INTO scene_"""+location['postgis_db']+""" (ingestion_time, mission_id, pass) VALUES (%(ingestion_time)s, %(mission_id)s, %(pass)s);"""

    logger.info("Loop scenes")

    for scene in scenes:
        if not scene.endswith('.zip'):
            continue

        ingestion_time = datetime.strptime(scene.split('_')[4],'%Y%m%dT%H%M%S')

        zip=zipfile.ZipFile(os.path.join(sarIn,scene))

        contents=zip.namelist()
        subs='vv-'+datetime.strftime(ingestion_time,'%Y%m%dt%H%M%S')
        contents = [x for x in contents if len(x.split('/'))>2]
        res = [x for x in contents if re.search(subs, x.split('/')[2]) and x.split('/')[1] == 'annotation']

        xml=zip.read(res[0])
        xdict = xmltodict.parse(xml)

        logger.info("Insert metadata for "+scene)

        cur.execute(INSERT,
            {'table':'scene_'+location['postgis_db'],
                'ingestion_time': ingestion_time,
                'mission_id': xdict['product']['adsHeader']['missionId'],
                'pass': xdict['product']['generalAnnotation']['productInformation']['pass']})

    conn.commit()
    cur.close()
    conn.close()

    logger.info("Finished insert")
