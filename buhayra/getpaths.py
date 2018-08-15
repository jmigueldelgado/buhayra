from os.path import expanduser
import sys
import socket

if socket.gethostname()=='mondego':
    home = {
        'home' : expanduser("~"),
        'scratch' : expanduser("~") + '/scratch',
        'proj' : expanduser("~") + '/proj/buhayra',
        'parameters' : expanduser("~") + '/proj/buhayra/buhayra/parameters'}
elif socket.gethostname()=='ubuntuserver':
    home = {
        'home' : expanduser("~"),
        'scratch' : 'None',
        'proj' : expanduser("~") + '/proj/buhayra',
        'parameters' : expanduser("~") + '/proj/buhayra/buhayra/parameters'}
else:
    home = {
        'home' : expanduser("~"),
        'scratch' : '/mnt/scratch/martinsd',
        'proj' : expanduser("~") + '/proj/buhayra',
        'parameters' : expanduser("~") + '/proj/buhayra/buhayra/parameters'}

pyt = home['home'] + "/local/miniconda2/envs/gdal/bin/python"
pyGdal = home['home'] + "/local/miniconda2/envs/gdal/bin/python"
pyFmask = home['home'] + "/local/miniconda2/envs/fmask/bin/python"

gdalPol = home['home'] + "/local/miniconda2/envs/gdal/bin/gdal_polygonize.py"
gdalMerge = home['home'] + "/local/miniconda2/envs/gdal/bin/gdal_merge.py"
gdalBuildvrt = home['home'] + "/local/miniconda3/envs/fiorio/bin/gdalbuildvrt"
fmaskMakeAngles = home['home'] + "/local/miniconda2/envs/fmask/bin/fmask_sentinel2makeAnglesImage.py"
fmaskStack = home['home'] + "/local/miniconda2/envs/fmask/bin/fmask_sentinel2Stacked.py"


proj = home['proj']
scratch= home['scratch']


sardir=scratch+"/s1a_scenes"
s2adir=scratch+"/s2a_scenes"

s2aIn=s2adir+"/in"
s2aIn=s2adir+"/in"
s2aOut=s2adir+"/out"

sarIn=sardir+"/in"
sarOut=sardir+"/out"

polOut=scratch + "/watermasks"
procOut=scratch + "/processed_watermasks"

MONGO_HOST = "141.89.96.184"
MONGO_DB = "sar2watermask"
MONGO_PORT = 27017

sys.path.insert(0, home['parameters'])
from buhayra.credentials import *
