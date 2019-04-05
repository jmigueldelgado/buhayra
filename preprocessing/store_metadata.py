import psycopg2
from buhayra.getpaths import *
from buhayra.credentials import *
import buhayra.utils as utils
import os
import zipfile
import xmltodict
import datetime

ingestion_time = datetime.datetime.strptime('20181007T081706','%Y%m%dT%H%M%S')
scene=utils.select_scene_ingestion_time(ingestion_time,sarIn)

zip=zipfile.ZipFile(os.path.join(sarIn,scene[0]))

contents=zip.namelist()
subs='vv-'+datetime.datetime.strftime(ingestion_time,'%Y%m%dt%H%M%S')
contents = [x for x in contents if len(x.split('/'))>2]
res = [x for x in contents if re.search(subs, x.split('/')[2]) and x.split('/')[1] == 'annotation']

xml=z.read(res[0])
xdict = xmltodict.parse(xml)

conn = psycopg2.connect(host=postgis_host,dbname=watermasks,user=postgis_user,password=postgis_pass)
cur = conn.cursor()
SQL= """INSERT INTO scene_ned
    ... (ingestion_time, mission_id, pass)
    ...VALUES (%(date)s, %(str)s, %(str)s);"""

cur.execute(SQL,
    {'ingestion_time': ingestion_time,
        'mission_id': xdict['product']['adsHeader']['missionId'],
        'pass': xdict['product']['generalAnnotation']['productInformation']['pass']})
