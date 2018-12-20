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

def load_random_lazy(h,w,hchunk,wchunk):
    return da.random.random((h,w),chunks=(hchunk,wchunk))*3


def load_lazy_raster(f):
    logger = logging.getLogger('root')
    with rasterio.open(vegIn + '/' +f,'r') as ds:
        r=da.from_array(ds.read(1),(2700,2700))
        out_transform = ds.transform

    logger.info("Loading tif and creating lazy array")
    logger.info("Chunked lazy array is "+str(r.nbytes/10**6)+" MB")

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

def wrap_glcm_matrix_dissimilarity_mean(X,window_shape,levels):
    h, w, nrows, ncols = X.shape
    out=np.zeros((h,w,2,1),dtype=np.uint8)
    for i,j in np.ndindex(X[:,:,0,0].shape):
        glcm = greycomatrix(X[i,j,:,:], [1], [0, np.pi/4, np.pi/2, 3*np.pi/4], levels,normed=False,symmetric=True)
        GLCM=np.sum(glcm,(2,3))
        leveli, levelj = GLCM.shape
        out[i,j,0,:]=greycoprops(GLCM.reshape(leveli,levelj,1,1), 'dissimilarity')[0,0]
        out[i,j,1,:]=glcm_mean(GLCM.reshape(leveli,levelj,1,1))
    return out

        #
        # glcm_mean_ = glcm_mean(GLCM)
        # glcm_variance_ = glcm_variance(GLCM,glcm_mean_)
        # glcmi = [glcm_mean_,
        #     glcm_variance_,
        #     greycoprops(glcm, 'contrast')[0,0],
        #     greycoprops(glcm, 'dissimilarity')[0,0],
        #     greycoprops(glcm, 'homogeneity')[0,0],
        #     greycoprops(glcm, 'energy')[0,0],
        #     greycoprops(glcm, 'correlation')[0, 0],
        #     greycoprops(glcm, 'ASM')[0, 0]]
        # predictor[i]=glcmi

def wrap_mean(matrix):
    matrix=matrix.reshape(matrix.shape[0:2])
    return np.array([np.mean(matrix)])

def loadings_and_explained_variance(X,PCA):
    pca = PCA(n_components=3)
    pcafit=pca.fit(X)
    eigenvectors = pcafit.components_
    var = pcafit.explained_variance_ratio_
    return eigenvectors, var
