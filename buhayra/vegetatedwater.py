import numpy as np
from buhayra.getpaths import *
import rasterio
import logging
import os
import re
import datetime

def load_raster(f):
    with rasterio.open(vegIn + '/' + f,'r') as ds:
        r=ds.read(1)
        out_transform=ds.transform
    return r, out_transform


def select_last_tiff():
    logger = logging.getLogger('root')
    if(len(listdir(vegIn))<1):
        logger.info(vegIn+" is empty! Nothing to do. Exiting and returning None.")
        f=None
    else:
        timestamp=list()
        scenes=list()
        for scn in listdir(vegIn):
            if re.search('.tif$',scn):
                scenes.append(scn)
                timestamp.append(datetime.datetime.strptime(scn.split('_')[4],'%Y%m%dT%H%M%S'))
        f=scenes[timestamp.index(max(timestamp))]
    return(f)
