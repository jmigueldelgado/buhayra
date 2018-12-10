import numpy as np
import buhayra.vegetatedwater as veggie
from buhayra.getpaths import *
import time
from sklearn.preprocessing import scale, minmax_scale
from dask.distributed import Client, progress, LocalCluster
import dask.array as da
from dask_ml.decomposition import PCA
# from sklearn.decomposition import PCA
import dask
import rasterio


cluster = LocalCluster(processes=False,n_workers=2,threads_per_worker=4, memory_limit='1GB')
client = Client(cluster)

x = da.random.random((5000, 5000), chunks=(1000, 1000))
xx=np.random.random((100,100))

X_std = (x - np.amin(x)) / (np.amax(x) - np.amin(x))
X_scaled = dask.array.round(X_std * (255 - 0) + 0)
x=X_scaled.compute()
xuint = x.astype='uint8'

get_glcm_predictors = dask.delayed(veggie.get_glcm_predictors)

predictor=get_glcm_predictors(xuint)

out=predictor.compute()
client.close()

pca = PCA(n_components=3)
pcafit=pca.fit(x)
eigenvectors = pcafit.components_
z=x.mean()
z.compute()


f=veggie.select_last_tiff()

client.close()
cluster.close()

# %timeit
# start0=time.perf_counter()
with rasterio.open(vegIn + '/' +f,'r') as ds:
    x=da.from_array(ds.read(1),(round(ds.shape[0]/20), round(ds.shape[1]/20)))
    lazymean=x.mean()
    # out.visualize(filename='da_mean.svg')
# time.perf_counter()-start0



start0=time.perf_counter()
out=lazymean.compute()
time.perf_counter()-start0

out




with rasterio.open(vegIn + '/' +f,'r') as ds:
    x=ds.read(1)


start0=time.perf_counter()
out=x.mean()
time.perf_counter()-start0


ds.dtypes

r = da.from_delayed(lazy_raster,ds.shape,ds.dtypes[0])

r.nbytes/10**9

r.shape
r=r[0:4000,0:4000]

x = da.from_array(r, chunks=(round(r.shape[0]/4), round(r.shape[1]/4)))

cluster = LocalCluster(processes=False,n_workers=2,threads_per_worker=2, memory_limit='1GB')
client = Client(cluster)

client.restart()

# r = np.random.rand(4000,4000)
x = da.from_array(r[], chunks=(5000, 5000))

# x = da.random.random((2000, 2000), chunks=(500, 500))
start0=time.perf_counter()
z=scale(r)
time.perf_counter()-start0




pca = PCA(n_components=2)
pcafit=pca.fit(da.from_array(z,chunks=(500,500)))
eigenvectors = pcafit.components_

out=veggie.get_loadings_and_explained_variance(da.from_array(z,chunks=(500,500)),PCA)

client.close()
cluster.close()
