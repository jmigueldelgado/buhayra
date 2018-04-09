from os.path import expanduser

if expanduser("~")=='/home/delgado':
    home['scratch'] = expanduser("~") + '/scratch'
else:
    home['scratch'] = '/mnt/scratch/martinsd'

pyt = home['home'] + "/local/miniconda2/envs/gdal/bin/python"
gdalPol = home['home'] + "/local/miniconda2/envs/gdal/bin/gdal_polygonize.py"
proj = home['proj']
scratch= home['scratch']
    
sardir=scratch+"/s1a_scenes"
sarIn=sardir+"/in"
sarOut=sardir+"/out"
polOut=scratch + "/watermasks"

MONGO_HOST = "141.89.96.184"
MONGO_DB = "sar2watermask"
MONGO_PORT = 27017

