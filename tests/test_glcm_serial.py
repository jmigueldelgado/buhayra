
import numpy as np
import time
import dask.array as da
from dask import compute, delayed
import dask.threaded
from distributed import Client,LocalCluster
window_shape=(3,3)
levels=256
from skimage.feature import greycomatrix, greycoprops

def wrap_glcm_matrix_dissimilarity(X,window_shape,levels):
    h, w, nrows, ncols = X.shape
    out=np.zeros((h,w,1,1),dtype=np.uint8)
    for i,j in np.ndindex(X[:,:,0,0].shape):
        glcm = greycomatrix(X[i,j,:,:], [1], [0, np.pi/4, np.pi/2, 3*np.pi/4], levels,normed=False,symmetric=True)
        GLCM=np.sum(glcm,(2,3))
        leveli, levelj = GLCM.shape
        out[i,j,:,:]=greycoprops(GLCM.reshape(leveli,levelj,1,1), 'dissimilarity')[0,0]
    return out

isize=500
jsize=500

X = np.random.random((isize, jsize))*3
excess=(X.shape[0]%window_shape[0],X.shape[1]%window_shape[1])
X = X[0:(X.shape[0]-excess[0]),0:(X.shape[1]-excess[1])]
X=X.astype('uint')
h, w = X.shape
nrows=window_shape[0]
ncols=window_shape[1]
X=X.reshape(h//nrows, nrows,h*w//(ncols*nrows*(h//nrows)), ncols).swapaxes(1,2)

i=time.time()
diss = wrap_glcm_matrix_dissimilarity(X,window_shape,levels)
time.time()-i
