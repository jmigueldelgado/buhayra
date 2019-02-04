from shapely.geometry import mapping, Polygon, shape
from shapely.ops import cascaded_union, transform
import os
import pyproj
import fiona
import rasterio
import numpy as np
from buhayra.getpaths import *
from rasterio.features import sieve, shapes

f= '/home/delgado/proj/buhayra/preprocessing/occurrence_40W_0N.tif'


with rasterio.open(f,'r') as ds:
    src=ds.read(1)
    src[src>1]=1
    sieved = sieve(src, 10, out=np.zeros(src.shape, src.dtypes[0]))
    with rasterio.open(f[:-4]+'_bin.tif','w',driver='GTiff',height=src.shape[0],width=src.shape[1],count=1,dtype=rasterio.ubyte,transform=ds.transform) as dsout:
        dsout.write(src.astype(rasterio.ubyte),1)

    # polys=list()
    #
    # for pol, value in features.shapes(r, transform=ds.transform):
    #     if value==1:
    #         polys.append(shape(pol))
    #
    # jrc_featcoll = cascaded_union(polys)
    #
    #
    # project = partial(
    #     pyproj.transform,
    #     pyproj.Proj(init='epsg:4326'),
    #     pyproj.Proj(init='epsg:32629'))
    #
    # jrc_spt_utm=transform(project,jrc_featcoll)
