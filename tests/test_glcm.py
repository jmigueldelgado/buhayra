
import numpy as np
import time
import dask.array as da
from dask import compute, delayed
import dask.threaded
from skimage.util.shape import view_as_windows, view_as_blocks


X = np.random.random((500, 500))
dX = da.random.random((500, 500), chunks=(50, 50))

da.map_blocks(view_as_windows,dX,(10,10),chunks=(50,50,10,10),new_axis=[2,3])


pcafit=pca.fit(predictors[0])
# results = compute(pcafit, scheduler='threads')
time.time()-i


eigenvectors = pcafit.components_

# no dask

f=veggie.select_last_tiff()
with rasterio.open(vegIn + '/' +f,'r') as ds:
    x=ds.read(1)


# no dask
i=time.time()
X_std = (x - np.amin(x)) / (np.amax(x) - np.amin(x))
X_scaled = np.round(X_std * (255 - 0) + 0)
xuint = X_scaled.astype('uint8')
results = veggie.glcm_predictors(xuint)
time.time()-i


########

out=predictor.compute()
client.close()

pca = PCA(n_components=3)
pcafit=pca.fit(x)
eigenvectors = pcafit.components_
z=x.mean()
z.compute()



# client.close()
# cluster.close()

# %timeit
# start0=time.perf_counter()
with rasterio.open(vegIn + '/' +f,'r') as ds:
    x=da.from_array(ds.read(1),(round(ds.shape[0]/5), round(ds.shape[1]/5)))
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
