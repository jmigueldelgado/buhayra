from skimage.feature import greycomatrix, greycoprops
import numpy as np
import rasterio

def load_raster(f):
    with rasterio.open(vegOut + '/' + f,'r') as ds:
        r=ds.read(1)
        out_transform=ds.transform
    return r, out_transform

def
    glcm = greycomatrix(patch, [5], [0], 256, symmetric=True, normed=True)
