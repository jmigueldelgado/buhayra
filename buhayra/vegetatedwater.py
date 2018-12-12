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

def get_loadings_and_explained_variance(X,PCA):
    pca = PCA(n_components=3)
    pcafit=pca.fit(X)
    eigenvectors = pcafit.components_
    var = pcafit.explained_variance_ratio_
    return eigenvectors, var


def get_glcm_predictors(image):
    window_shape=(3,3)
    new_image = image[:-(image.shape[0]%window_shape[0]),:-(image.shape[1]%window_shape[1])]

    B=view_as_blocks(new_image, window_shape)
    X=B.reshape((B.shape[0]*B.shape[1],B.shape[2],B.shape[3]))
    predictor=np.empty((X.shape[0],5))

    for i in range(1000):#X.shape[0]):
        glcm = greycomatrix(X[i,:,:], [1], [0, np.pi/4, np.pi/2, 3*np.pi/4], 256,symmetric=True)
        GLCM=np.sum(glcm,(2,3))
        glcmi = [np.mean(GLCM,axis=0)[0],np.std(GLCM)**2,greycoprops(glcm, 'homogeneity')[0,0],greycoprops(glcm, 'dissimilarity')[0,0],greycoprops(glcm, 'correlation')[0, 0]]
        predictor[i]=glcmi

    return(predictor)
