import os
import sys
from datetime import datetime
import logging
from buhayra.getpaths import *
from buhayra.credentials import *
import subprocess
import psycopg2
import IPython

def insert_into_postgres(src_path,o_std,o_err):
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
        location['postgis_db'],
        '-append',
        '-skipfailures']

    logger.info('insering into pg:')
    logger.info(src_path)

#    IPython.embed()

    r = subprocess.Popen(call,
        stdout=o_std,
        stderr=o_err,
        preexec_fn=os.setpgrp)

def insert_into_postgres_no_geom(ls):
    logger = logging.getLogger('root')
    conn = psycopg2.connect(host=postgis_host,
        user=postgis_user,
        password=postgis_pass,
        database='watermasks')
    with conn.cursor() as curs:
        for d in ls:
            # IPython.embed()
            keys = d.keys()
            columns = ','.join(keys)
            values = ','.join(['%({})s'.format(k) for k in keys])
            insert_schema = 'insert into '+ location['region'] +' ({0}) values ({1})'.format(columns, values)
            insert_string=curs.mogrify(insert_schema, d)
            try:
                curs.execute(insert_string)
            except (Exception, psycopg2.DatabaseError) as error:
                print("Error: %s" % error)
                conn.rollback()
                curs.close()
                return 1
            conn.commit()
 
        logger.info('execute_mogrify() done')
        curs.close()
        conn.close()
