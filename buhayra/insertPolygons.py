import os
import sys
from datetime import datetime
import logging
from buhayra.getpaths import *
from buhayra.credentials import *
import subprocess
import psycopg2

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

    r = subprocess.Popen(call,
        stdout=o_std,
        stderr=o_err,
        preexec_fn=os.setpgrp)

def insert_into_postgres_no_geom(ls)
    conn = psycopg2.connect(host=postgis_host,
        user=postgis_user,
        password=postgis_pass,
        database='watermasks')

    for d in ls:
        keys = d.keys()
        columns = ','.join(keys)
        values = ','.join(['%({})s'.format(k) for k in keys])
        insert = 'insert into '+ location['region'] +' ({0}) values ({1})'.format(columns, values)
        print cursor.mogrify(insert, d)
