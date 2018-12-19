import numpy as np
from buhayra.getpaths import *
import logging
import os
import rasterio
import re
import datetime
from skimage.util.shape import view_as_windows, view_as_blocks
from skimage.feature import greycomatrix, greycoprops
import dask.array as da

def load_lazy_raster(f):
    with rasterio.open(vegIn + '/' +f,'r') as ds:
        r=da.from_array(ds.read(1),(ds.shape[0]//10, ds.shape[1]//10))
        out_transform = ds.transform
    # with rasterio.open(vegIn + '/' + f,'r') as ds:
    #     r=ds.read(1)
    #     out_transform=ds.transform
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
    out=np.zeros((h,w,levels,levels),dtype=np.uint8)
    for i,j in np.ndindex(X[:,:,0,0].shape):
        glcm = greycomatrix(X[i,j,:,:], [1], [0, np.pi/4, np.pi/2, 3*np.pi/4], levels,normed=False,symmetric=True)
        out[i,j,:,:]=np.sum(glcm,(2,3))
    return out

def glcm_mean(matrix):
    matrix=matrix.reshape(matrix.shape[0:2])
    i = np.arange(matrix.shape[0])
    return np.sum(i*matrix[i,0])

def glcm_variance(matrix,glcm_mean_):
    matrix=matrix.reshape(matrix.shape[0:2])
    i = np.arange(matrix.shape[0])
    return np.sum(matrix[i,0]*(i-glcm_mean_)**2)

def wrap_glcm_mean(matrix):
    h, w, leveli, levelj = matrix.shape
    out=np.empty((h,w,1,1))
    for i,j in np.ndindex(matrix[:,:,0,0].shape):
        out[i,j,:,:]=glcm_mean(matrix[i,j,:,:].reshape(leveli,levelj,1,1))
    return out

def wrap_glcm_variance(matrix,glcm_mean_matrix):
    h, w, leveli, levelj = matrix.shape
    out=np.empty((h,w,1,1))
    for i,j in np.ndindex(matrix[:,:,0,0].shape):
        out[i,j,:,:]=glcm_variance(matrix[i,j,:,:].reshape(leveli,levelj,1,1),glcm_mean_matrix[i,j,0,0])
    return out

def wrap_glcm_dissimilarity(matrix):
    h, w, leveli, levelj = matrix.shape
    out=np.empty((h,w,1,1))
    for i,j in np.ndindex(matrix[:,:,0,0].shape):
        out[i,j,:,:]=greycoprops(matrix[i,j,:,:].reshape(leveli,levelj,1,1), 'dissimilarity')[0,0]
    return out

def wrap_glcm_contrast(matrix):
    h, w, leveli, levelj = matrix.shape
    out=np.empty((h,w,1,1))
    for i,j in np.ndindex(matrix[:,:,0,0].shape):
        out[i,j,:,:]=greycoprops(matrix[i,j,:,:].reshape(leveli,levelj,1,1), 'contrast')[0,0]
    return out

def wrap_glcm_homogeneity(matrix):
    h, w, leveli, levelj = matrix.shape
    out=np.empty((h,w,1,1))
    for i,j in np.ndindex(matrix[:,:,0,0].shape):
        out[i,j,:,:]=greycoprops(matrix[i,j,:,:].reshape(leveli,levelj,1,1), 'homogeneity')[0,0]
    return out


def wrap_mean(matrix):
    matrix=matrix.reshape(matrix.shape[0:2])
    return np.array([np.mean(matrix)])
