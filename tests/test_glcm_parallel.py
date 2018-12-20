
import numpy as np
import time
import dask.array as da
from dask import compute, delayed, visualize
import dask.threaded
from buhayra.vegetatedwater import *
from distributed import Client,LocalCluster
import logging


def glcm_with_matrix():
    logger = logging.getLogger('root')
    window_shape=(3,3)
    levels=256

    # f=select_last_tiff()
    # (dX,out_transform)=load_lazy_raster(f)
    dX=load_random_lazy(1000,1000,200,200)
    # dX=load_random_lazy(300,300,150,300)

    dX_std = (dX - np.amin(dX)) / (np.amax(dX) - np.amin(dX))
    dX = dask.array.round(dX_std * (255 - 0) + 0)
    dX = dX.astype('uint8')

    logger.info("Trimming array to a multiple of three")
    excess=(dX.shape[0]%window_shape[0],dX.shape[1]%window_shape[1])
    dX = dX[0:(dX.shape[0]-excess[0]),0:(dX.shape[1]-excess[1])]
    h, w = dX.shape
    nrows=window_shape[0]
    ncols=window_shape[1]
    dX=dX.reshape(h//nrows, nrows,h*w//(ncols*nrows*(h//nrows)), ncols).swapaxes(1,2)
    chunks_matrix = (10,3,levels,levels)
    # chunks_matrix = (dX.shape[0]/2,dX.shape[1],levels,levels)
    lazymatrix = da.map_blocks(wrap_glcm_matrix,dX,window_shape,levels,chunks=chunks_matrix)

    logger.info("Size of lazy glcm matrix is "+ str(lazymatrix.nbytes/10**9)+" GB")

    ### until now best combination of workers and threads
    # c=LocalCluster(processes=False,n_workers=4,threads_per_worker=5,memory_limit='7GB')
    # client = Client(c)

    chunks_props = (200,200,1,1)
    # chunks_props = (dX.shape[0]/2,dX.shape[1],1,1)
    lazydiss = da.map_blocks(wrap_glcm_dissimilarity,lazymatrix,chunks=chunks_props)
    lazymean = da.map_blocks(wrap_glcm_mean,lazymatrix,chunks=chunks_props)
    lazyprops = da.dstack((lazydiss,lazymean))

    # lazydiss=da.reshape(lazydiss,(lazydiss.shape[0]*lazydiss.shape[1],1))
    # lazymean=da.reshape(lazymean,(lazymean.shape[0]*lazymean.shape[1],1))
    # lazyprops = da.hstack((lazydiss,lazymean))

    # lazydiss.nbytes/10**6
    # i=time.time()
    glcm_props=compute(lazyprops, scheduler='threads')
    # lazyprops.visualize(filename='glcm.svg')
    logger.info("Finished glcm computation with huge matrix generation.")


def glcm_plus_props():
    logger = logging.getLogger('root')
    window_shape=(3,3)
    levels=256

    # f=select_last_tiff()
    # (dX,out_transform)=load_lazy_raster(f)
    dX=load_random_lazy(1000,1000,200,200)
    # dX=load_random_lazy(300,300,150,300)

    dX_std = (dX - np.amin(dX)) / (np.amax(dX) - np.amin(dX))
    dX = dask.array.round(dX_std * (255 - 0) + 0)
    dX = dX.astype('uint8')

    logger.info("Trimming array to a multiple of three")
    excess=(dX.shape[0]%window_shape[0],dX.shape[1]%window_shape[1])
    dX = dX[0:(dX.shape[0]-excess[0]),0:(dX.shape[1]-excess[1])]
    h, w = dX.shape
    nrows=window_shape[0]
    ncols=window_shape[1]
    dX=dX.reshape(h//nrows, nrows,h*w//(ncols*nrows*(h//nrows)), ncols).swapaxes(1,2)

    chunks_props = (200,200,1,1)
    # chunks_props = (dX.shape[0]/2,dX.shape[1],1,1)
    lazyprops = da.map_blocks(wrap_glcm_matrix_dissimilarity_mean,dX,window_shape,levels,chunks=chunks_props)

    # lazydiss.nbytes/10**6
    # i=time.time()
    glcm_props=compute(lazyprops, scheduler='threads')
    # lazyprops.visualize(filename='glcm.svg')
    logger.info("Finished glcm computation with no huge matrix generation.")


def glcm_serial_props():
    logger = logging.getLogger('root')
    window_shape=(3,3)
    levels=256
    dX = np.random.random((1000, 1000))*3

    dX_std = (dX - np.amin(dX)) / (np.amax(dX) - np.amin(dX))
    dX = np.round(dX_std * (255 - 0) + 0)
    dX = dX.astype('uint8')

    logger.info("Trimming array to a multiple of three")
    excess=(dX.shape[0]%window_shape[0],dX.shape[1]%window_shape[1])
    dX = dX[0:(dX.shape[0]-excess[0]),0:(dX.shape[1]-excess[1])]
    h, w = dX.shape
    nrows=window_shape[0]
    ncols=window_shape[1]
    dX=dX.reshape(h//nrows, nrows,h*w//(ncols*nrows*(h//nrows)), ncols).swapaxes(1,2)

    glcm_props = wrap_glcm_matrix_dissimilarity_mean(dX,window_shape,levels)

    logger.info("Finished serial glcm computation.")
