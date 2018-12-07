from skimage.feature import greycomatrix, greycoprops
import numpy as np
import rasterio
from buhayra.getpaths import *
f='S1A_IW_GRDH_1SDV_20181019T081732_20181019T081757_024202_02A5C9_4A4B.tif'

def load_raster(f):
    with rasterio.open(vegIn + '/' + f,'r') as ds:
        r=ds.read(1)
        out_transform=ds.transform
    return r, out_transform

def
    glcm = greycomatrix(patch, [5], [0], 256, symmetric=True, normed=True)
