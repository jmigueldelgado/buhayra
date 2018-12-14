
import numpy as np
import time
import dask.array as da
from dask import compute, delayed
import dask.threaded
from skimage.util.shape import view_as_windows, view_as_blocks
import buhayra.vegetatedwater as veggie
from skimage.feature import greycomatrix, greycoprops

window_shape=(3,3)
levels=256


def wrap_glcm_dissimilarity(matrix):
    h, w, leveli, levelj = matrix.shape
    out=np.empty((h,w,1,1))
    for i,j in np.ndindex(matrix[:,:,0,0].shape):
        out[i,j,:,:]=greycoprops(matrix[0,0,:,:].reshape(leveli,levelj,1,1), 'dissimilarity')[0,0]
    return out

def wrap_glcm_matrix(X,window_shape,levels):
    h, w, nrows, ncols = X.shape
    out=np.empty((h,w,levels,levels))
    for i,j in np.ndindex(X[:,:,0,0].shape):
        glcm = greycomatrix(X[i,j,:,:], [1], [0, np.pi/4, np.pi/2, 3*np.pi/4], levels,normed=False,symmetric=True)
        out[i,j,:,:]=np.sum(glcm,(2,3))
    return out


def wrap_mean(X):
    return np.array([[np.mean(X)]])

X = np.random.random((12, 12))*3
X=X.astype('uint')
h, w = X.shape
nrows=window_shape[0]
ncols=window_shape[1]
X=X.reshape(h//nrows, nrows,h*w//(ncols*nrows*(h//nrows)), ncols).swapaxes(1,2)

i=time.time()
matrix = wrap_glcm_matrix(X,window_shape,levels)
time.time()-i



dX = da.random.random((120, 120), chunks=(60, 60))*3
excess=(dX.shape[0]%window_shape[0],dX.shape[1]%window_shape[1])
dX = dX[0:(dX.shape[0]-excess[0]),0:(dX.shape[1]-excess[1])]
dX=dX.astype('uint')
h, w = dX.shape
nrows=window_shape[0]
ncols=window_shape[1]
dX=dX.reshape(h//nrows, nrows,h*w//(ncols*nrows*(h//nrows)), ncols).swapaxes(1,2)
lazymatrix = da.map_blocks(wrap_glcm_matrix,dX,window_shape,levels,chunks=(10,10,levels,levels))
### persist lazy matrix here!!! http://distributed.dask.org/en/latest/memory.html#difference-with-dask-compute

lazydiss = da.map_blocks(wrap_glcm_dissimilarity,lazymatrix,chunks=(20,20,1,1))

i=time.time()
predictor=compute(lazydiss, scheduler='threads')
time.time()-i

predictor[0].shape






def loadings_and_explained_variance(X,PCA):
    pca = PCA(n_components=3)
    pcafit=pca.fit(X)
    eigenvectors = pcafit.components_
    var = pcafit.explained_variance_ratio_
    return eigenvectors, var

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
    i = np.arange(matrix.shape[0])
    return np.sum(i*matrix[i,0])

def glcm_variance(matrix,glcm_mean_):
    i = np.arange(matrix.shape[0])
    return np.sum(matrix[i,0]*(i-glcm_mean_)**2)
