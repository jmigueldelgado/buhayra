import numpy as np
from buhayra.getpaths import *
import logging
import os
import rasterio
import re
import datetime
from skimage.util.shape import view_as_windows, view_as_blocks
from skimage.feature import greycomatrix, greycoprops

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

def wrap_glcm_matrix(X,window_shape,levels):
    h, w, nrows, ncols = X.shape
    out=np.empty((h,w,levels,levels))
    for i,j in np.ndindex(X[:,:,0,0].shape):
        glcm = greycomatrix(X[i,j,:,:], [1], [0, np.pi/4, np.pi/2, 3*np.pi/4], levels,normed=False,symmetric=True)
        out[i,j,:,:]=np.sum(glcm,(2,3))
    return out

def wrap_glcm_dissimilarity(matrix):
    h, w, leveli, levelj = matrix.shape
    out=np.empty((h,w,1,1))
    for i,j in np.ndindex(matrix[:,:,0,0].shape):
        out[i,j,:,:]=greycoprops(matrix[0,0,:,:].reshape(leveli,levelj,1,1), 'dissimilarity')[0,0]
    return out
