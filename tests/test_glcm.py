import matplotlib.pyplot as plt
from skimage.feature import greycomatrix, greycoprops
from skimage import data
from sklearn.decomposition import PCA
from skimage.util.shape import view_as_windows, view_as_blocks
import numpy as np
import buhayra.vegetatedwater as veggie

f=veggie.select_last_tiff()

r, out_transform = veggie.load_raster(f)

##### test PCA in parallel
# from dask_ml.decomposition import PCA


from dask.distributed import Client, progress, LocalCluster
import dask.array as da
cluster = LocalCluster(processes=False,n_workers=1,threads_per_worker=8)
client = Client(cluster)

from sklearn import preprocessing
from sklearn import datasets

#open camera image
#iris = datasets.load_iris()
#XX = preprocessing.scale(iris.data)

dX = da.from_array(r, chunks=(2000,2000))


dXscaled = dX.map_blocks(preprocessing.scale)
dXscaled.compute() ## OR
dXscaled.compute(schedule='single-threaded')


loadings,variance = get_loadings_and_explained_variance(XX,PCA)
loadings[0,]
variance

def get_loadings_and_explained_variance(X,PCA):
    pca = PCA(n_components='mle')
    pcafit=pca.fit(X)
    eigenvectors = pcafit.components_
    # np.linalg.norm(cmps[2,:])
    var = pcafit.explained_variance_ratio_
    return eigenvectors, var




######  glcm on single cpu
image = data.camera()


import time
start=time.process_time()
predictors=get_glcm_predictors(image)
time.process_time()-start

def get_glcm_predictors(image):
    window_shape=(3,3)
    new_image = image[:-(image.shape[0]%window_shape[0]),:-(image.shape[1]%window_shape[1])]

    B=view_as_blocks(new_image, window_shape)
    X=B.reshape((B.shape[0]*B.shape[1],B.shape[2],B.shape[3]))
    predictor=np.empty((X.shape[0],5))

    for i in range(1000):#X.shape[0]):
        glcm = greycomatrix(X[i,:,:], [1], [0, np.pi/4, np.pi/2, 3*np.pi/4, np.pi, 5*np.pi/4, 3*np.pi/2,2*np.pi], 256)
        GLCM=np.sum(glcm,(2,3))
        glcmi = [np.mean(GLCM),np.std(GLCM)**2,greycoprops(glcm, 'homogeneity')[0,0],greycoprops(glcm, 'dissimilarity')[0,0],greycoprops(glcm, 'correlation')[0, 0]]
        predictor[i]=glcmi

    return(predictor)
