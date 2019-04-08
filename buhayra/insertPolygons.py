import os
import sys
from datetime import datetime
import logging
from buhayra.getpaths import *
from buhayra.credentials import *
import subprocess


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
        location['postgis_db'],
        '-append',
        '-skipfailures']

    r = subprocess.Popen(call,
        stdout=o_std,
        stderr=o_err,
        preexec_fn=os.setpgrp)
