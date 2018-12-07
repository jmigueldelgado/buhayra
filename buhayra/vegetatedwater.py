from skimage.feature import greycomatrix, greycoprops
import numpy as np
import rasterio
from buhayra.getpaths import *

def load_raster(f):
    with rasterio.open(vegIn + '/' + f,'r') as ds:
        r=ds.read(1)
        out_transform=ds.transform
    return r, out_transform

