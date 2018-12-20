
import numpy as np
import time
import dask.array as da
from dask import compute, delayed
import dask.threaded
from distributed import Client,LocalCluster
window_shape=(3,3)
levels=256
from skimage.feature import greycomatrix, greycoprops



isize=1000
jsize=1000

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
