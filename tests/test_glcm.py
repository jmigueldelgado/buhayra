
import matplotlib.pyplot as plt
from skimage.feature import greycomatrix, greycoprops
from skimage import data
from sklearn.decomposition import PCA
from skimage.util.shape import view_as_windows
import numpy as np

##### test PCA in parallel
from dask_ml.decomposition import PCA
from dask.distributed import Client, progress
import dask.array as da

client = Client(processes=False, threads_per_worker=2,
            n_workers=1, memory_limit='2GB')

#open camera image
X = data.camera()
dX = da.from_array(X, chunks=X.shape)

pca = PCA(n_components=2)
pca.fit(dX)




######  glcm on single cpu

window_shape=(3,3)

B=view_as_windows(image, window_shape)
X=B.reshape((B.shape[0]*B.shape[1],B.shape[2],B.shape[3]))

predictor=list()

for i in range(10):
    glcm = greycomatrix(X[i,:,:], [1], [0, np.pi/4, np.pi/2, 3*np.pi/4, np.pi, 5*np.pi/4, 3*np.pi/2,2*np.pi], 256)
    GLCM=np.sum(glcm,(2,3))
    glcmi = [np.mean(GLCM),np.std(GLCM)**2,greycoprops(glcm, 'homogeneity')[0,0],greycoprops(glcm, 'dissimilarity')[0,0],greycoprops(glcm, 'correlation')[0, 0]]
    predictor.append(glcmi)

predictor
