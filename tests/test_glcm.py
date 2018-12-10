import numpy as np
import buhayra.vegetatedwater as veggie
import time
from sklearn.preprocessing import scale
from dask.distributed import Client, progress, LocalCluster
import dask.array as da
from dask_ml.decomposition import PCA

cluster = LocalCluster(processes=False,n_workers=1,threads_per_worker=3, memory_limit='2GB')
client = Client(cluster)

client.restart()


f=veggie.select_last_tiff()
r, out_transform = veggie.load_raster(f)

r = np.random.rand(4000,4000)
x = da.from_array(r, chunks=(500, 500))

# x = da.random.random((2000, 2000), chunks=(500, 500))
start0=time.perf_counter()
z=scale(x)
time.perf_counter()-start0

pca = PCA(n_components=2)
pcafit=pca.fit(da.from_array(z,chunks=(500,500)))
eigenvectors = pcafit.components_

out=veggie.get_loadings_and_explained_variance(da.from_array(z,chunks=(500,500)),PCA)

client.close()
cluster.close()
