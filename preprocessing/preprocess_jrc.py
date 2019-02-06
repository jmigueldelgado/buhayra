from shapely.geometry import mapping, Polygon, shape
from shapely.ops import cascaded_union, transform
import os
import pyproj
import fiona
import rasterio
import numpy as np
from buhayra.getpaths import *
from rasterio.features import sieve, shapes
from rasterio.mask import mask
import numpy as np


jrc_paths = ['/home/delgado/proj/buhayra/preprocessing/occurrence_40W_0N.tif',
    '/home/delgado/proj/buhayra/preprocessing/occurrence_50W_0N.tif',
    '/home/delgado/proj/buhayra/preprocessing/occurrence_40W_10S.tif',
    '/home/delgado/proj/buhayra/preprocessing/occurrence_50W_10S.tif']

with fiona.open('/home/delgado/proj/buhayra/preprocessing/semiarido.gpkg','r') as fio:
    semiarido=shape(next(iter(fio))['geometry'])

for path_i in jrc_paths:
    with rasterio.open(path_i,'r') as src:
        out_image, out_transform = mask(src,semiarido,all_touched=True,crop=True)
        out_meta = src.meta
    out_image[np.where(out_image>1)]=1
    raster = out_image[0]
    sieved = sieve(raster, 10, out=np.zeros(raster.shape, raster.dtype))
    with rasterio.open(path_i[:-4]+'_bin_sieved.tif','w',driver='GTiff',height=raster.shape[0],width=raster.shape[1],count=1,dtype=rasterio.ubyte,transform=out_transform) as dsout:
        dsout.write(sieved.astype(rasterio.ubyte),1)

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
