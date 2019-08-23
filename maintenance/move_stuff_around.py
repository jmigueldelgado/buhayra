import os
from buhayra.getpaths import *
import datetime
import re
import buhayra.utils as utils
import logging
import psycopg2

def rename_json():
    while(selectPattern(sarOut,'orrjson$')):
        f=selectPattern(sarOut,'orrjson$')
        os.rename(sarOut+'/'+f,sarOut+'/'+f[:-4]+'.json')

def move_proc(Y,M):
    folders = select_folders_year_month(Y,M,procOut)
    for folder in folders:
        if  not folder.startswith('S'):
            continue
        if not os.path.isdir(os.path.join(procOut,folder)):
            continue
        for filename in os.listdir(os.path.join(procOut,folder)):
            if filename.endswith('.tif'):
                if not os.path.isfile(os.path.join(sarOut,folder,filename)):
                    os.rename(os.path.join(procOut,folder,filename),os.path.join(sarOut,folder,filename))
                if not os.path.exists(os.path.join(sarOut,folder,filename[:-3]+'finished')):
                    open(os.path.join(sarOut,folder,filename[:-3]+'finished','w')).close()
            if filename.endswith('.json'):
                if not os.path.isfile(os.path.join(sarOut,folder,filename)):
                    os.rename(os.path.join(procOut,folder,filename),os.path.join(sarOut,folder,filename))


def move_tifs_to_folders():
    scenes=os.listdir(sarIn)
    outtifs = os.listdir(sarOut)
    proctifs = os.listdir(procOut)
    for scene in scenes:
        if scene.endswith('.finished'):
            continue
        if not os.path.isdir(os.path.join(sarOut,scene[:-4])):
            os.mkdir(os.path.join(sarOut,scene[:-4]))
        if not os.path.isdir(os.path.join(procOut,scene[:-4])):
            os.mkdir(os.path.join(procOut,scene[:-4]))
        for filename in outtifs:
            if filename.startswith(scene[:-4]) and (filename.endswith('.tif') or filename.endswith('.json') or filename.endswith('.finished')):
                src = os.path.join(sarOut,filename)
                trg = os.path.join(sarOut,scene[:-4],filename)
                os.rename(src,trg)
        for filename in proctifs:
            if filename.startswith(scene[:-4]) and (filename.endswith('.tif') or filename.endswith('.json') or filename.endswith('.finished')):
                src = os.path.join(procOut,filename)
                trg = os.path.join(procOut,scene[:-4],filename)
                os.rename(src,trg)

def rm_finished(src_path):
    logger = logging.getLogger('root')
    for scn in utils.list_scenes_finished(src_path):
        if os.path.isfile(os.path.join(src_path,scn[:-8]+'zip')):
            os.remove(os.path.join(src_path,scn[:-8]+'zip'))
            logger.info('Removing processed scene: ' + scn[:-8] + 'zip')

def update_db():
    logger = logging.getLogger('root')
    request="""INSERT INTO """ + location['region'] + """ SELECT ingestion_time, area, threshold, wmxjrc_area, id_jrc, source_id FROM """ + location['postgis_db'] + """ ON CONFLICT DO NOTHING;"""

    # following error occurs for this request:
        # NotNullViolation: null value in column "id" violates not-null constraint
        # DETAIL:  Failing row contains (null, 2019-03-23 18:26:52+01, 0, 0, 0, 644, S1A).

    logger.info("Connect to postgres with psycopg2")
    conn = psycopg2.connect(host=postgis_host,dbname='watermasks',user=postgis_user,password=postgis_pass)
    cur = conn.cursor()

    cur.execute(request)

    out=conn.commit()
    cur.close()
    conn.close()
    return out


def delete_old_geoms():
    cutoff_time = datetime.datetime.today()- datetime.timedelta(days=60)
    request = """ DELETE FROM """+location['region']+'_geom'+
                """WHERE ingestion_time < %(cutoff_time)s;"""

    logger.info("Connect to postgres with psycopg2")
    conn = psycopg2.connect(host=postgis_host,dbname='watermasks',user=postgis_user,password=postgis_pass)
    cur = conn.cursor()    cur.execute(request,{'cutoff_time': cutoff_time.strftime('%Y-%m-%d'})

    out=conn.commit()
    cur.close()
    conn.close()
    return out
