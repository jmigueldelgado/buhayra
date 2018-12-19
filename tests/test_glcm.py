
import numpy as np
import time
import dask.array as da
from dask import compute, delayed
import dask.threaded
from skimage.util.shape import view_as_windows, view_as_blocks
from buhayra.vegetatedwater import *
from skimage.feature import greycomatrix, greycoprops
from distributed import Client,LocalCluster


X = np.random.random((240, 240))*3
X=X.astype('uint')
h, w = X.shape
nrows=window_shape[0]
ncols=window_shape[1]
X=X.reshape(h//nrows, nrows,h*w//(ncols*nrows*(h//nrows)), ncols).swapaxes(1,2)

i=time.time()
matrix = wrap_glcm_matrix(X,window_shape,levels)
diss=wrap_glcm_dissimilarity(matrix)
glcm_mean_matrix=wrap_glcm_mean(matrix)
time.time()-i


window_shape=(3,3)
levels=256

dX = da.random.random((240, 240), chunks=(120, 120))*3
excess=(dX.shape[0]%window_shape[0],dX.shape[1]%window_shape[1])
dX = dX[0:(dX.shape[0]-excess[0]),0:(dX.shape[1]-excess[1])]
dX=dX.astype('uint')
h, w = dX.shape
nrows=window_shape[0]
ncols=window_shape[1]
dX=dX.reshape(h//nrows, nrows,h*w//(ncols*nrows*(h//nrows)), ncols).swapaxes(1,2)
lazymatrix = da.map_blocks(wrap_glcm_matrix,dX,window_shape,levels,chunks=(10,10,levels,levels))
### persist lazy matrix here!!! http://distributed.dask.org/en/latest/memory.html#difference-with-dask-compute



c=LocalCluster(processes=False)#,n_workers=1,threads_per_worker=2)
client = Client(c)

i=time.time()
lazymatrix = client.persist(lazymatrix)
lazydiss = da.map_blocks(wrap_glcm_dissimilarity,lazymatrix,chunks=(20,20,1,1))
# lazycontrast = da.map_blocks(wrap_glcm_contrast,lazymatrix,chunks=(20,20,1,1))
# lazyhomo = da.map_blocks(wrap_glcm_homogeneity,lazymatrix,chunks=(20,20,1,1))
lazymean = da.map_blocks(wrap_glcm_mean,lazymatrix,chunks=(20,20,1,1))
# lazyvar = da.map_blocks(wrap_glcm_variance,lazymatrix,lazymean,chunks=(20,20,1,1))
diss=lazydiss.compute()
# contrast=lazycontrast.compute()
# homo=lazyhomo.compute()
glcm_m=lazymean.compute()
# glcm_v=lazyvar.compute()
time.time()-i

client.close()
c.close()




i=time.time()
diss=compute(lazydiss, scheduler='threads')
time.time()-i



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
