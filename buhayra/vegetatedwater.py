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

def loadings_and_explained_variance(X,PCA):
    pca = PCA(n_components=3)
    pcafit=pca.fit(X)
    eigenvectors = pcafit.components_
    var = pcafit.explained_variance_ratio_
    return eigenvectors, var

def shape_of_trimmed_image(image,window_shape):
    return image.shape[0]-(image.shape[0]%window_shape[0]),image.shape[1]-(image.shape[1]%window_shape[1])

def list_of_3x3_blocks(image,window_shape):
    new_image = image[:-(image.shape[0]%window_shape[0]),:-(image.shape[1]%window_shape[1])]
    return view_as_blocks(new_image, window_shape)

def reshape_blocks(B):
    return B.reshape((B.shape[0]*B.shape[1],B.shape[2],B.shape[3]))


def glcm_predictors(X):
    predictor=np.empty((X.shape[0],8))

    for i in range(X.shape[0]):
        glcm = greycomatrix(X[i,:,:], [1], [0, np.pi/4, np.pi/2, 3*np.pi/4], 256,symmetric=True)
        GLCM=np.sum(glcm,(2,3))
        glcm_mean_ = glcm_mean(GLCM)
        glcm_variance_ = glcm_variance(GLCM,glcm_mean_)
        glcmi = [glcm_mean_,
            glcm_variance_,
            greycoprops(glcm, 'contrast')[0,0],
            greycoprops(glcm, 'dissimilarity')[0,0],
            greycoprops(glcm, 'homogeneity')[0,0],
            greycoprops(glcm, 'energy')[0,0],
            greycoprops(glcm, 'correlation')[0, 0],
            greycoprops(glcm, 'ASM')[0, 0]]
        predictor[i]=glcmi

    return(predictor)

def glcm_mean(matrix):
    # matrix=np.random.random((10,10))
    meani = np.empty((matrix.shape[0],1))
    for i in range(matrix.shape[0]):
        meani[i,0] = i*matrix[i,0]
    return np.sum(meani)

def glcm_variance(matrix,glcm_mean_):
    vari = np.empty((matrix.shape[0],1))
    for i in range(matrix.shape[0]):
        vari[i,0] = matrix[i,0]*(i-glcm_mean_)**2
    return np.sum(vari)
