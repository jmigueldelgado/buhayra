import subprocess
import modules.getPaths

pg='PG:"host=localhost dbname=watermasks user=' + postgis_user + ' password=' + postgis_pass + '"'
subprocess.call(['ogr2ogr','-f','PostgreSQL',pg,'/home/delgado/load_to_postgis','-nln','masks','-append'])
