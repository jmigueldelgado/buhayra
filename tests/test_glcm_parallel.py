
import numpy as np
import time
import dask.array as da
from dask import compute, delayed
import dask.threaded
from buhayra.vegetatedwater import *
from distributed import Client,LocalCluster
window_shape=(3,3)
levels=256


# f=select_last_tiff()
# (dX,out_transform)=load_lazy_raster(f)
# dX_std = (dX - np.amin(dX)) / (np.amax(dX) - np.amin(dX))
# dX = dask.array.round(dX_std * (255 - 0) + 0)
# dX = dX.astype('uint8')
# dX = dX[0:5000,0:5000]
isize=500
jsize=500

dX = da.random.random((isize, jsize), chunks=(200, 200))*3
excess=(dX.shape[0]%window_shape[0],dX.shape[1]%window_shape[1])
dX = dX[0:(dX.shape[0]-excess[0]),0:(dX.shape[1]-excess[1])]
dX=dX.astype('uint')
h, w = dX.shape
nrows=window_shape[0]
ncols=window_shape[1]
dX=dX.reshape(h//nrows, nrows,h*w//(ncols*nrows*(h//nrows)), ncols).swapaxes(1,2)
lazymatrix = da.map_blocks(wrap_glcm_matrix,dX,window_shape,levels,chunks=(20,20,levels,levels))


c=LocalCluster(processes=False,n_workers=2,threads_per_worker=2,memory_limit='500MB')
client = Client(c)
lazymatrix.nbytes/10**6
lazydiss = da.map_blocks(wrap_glcm_dissimilarity,lazymatrix,chunks=(200,200,1,1))

i=time.time()
diss=compute(lazydiss, scheduler='threads')
time.time()-i

client.close()
c.close()



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
