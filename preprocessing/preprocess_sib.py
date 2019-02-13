from shapely.geometry import mapping, Polygon, shape
from shapely.ops import cascaded_union, transform
import os
import pyproj
import fiona
import rasterio
import numpy as np
from buhayra.getpaths import *
from rasterio.features import sieve, shapes, rasterize
from rasterio.mask import mask
from rasterio.merge import merge
import numpy as np
import geojson


jrc_paths = ['/home/delgado/proj/buhayra/preprocessing/occurrence_40W_0N.tif',
    '/home/delgado/proj/buhayra/preprocessing/occurrence_50W_0N.tif',
    '/home/delgado/proj/buhayra/preprocessing/occurrence_40W_10S.tif',
    '/home/delgado/proj/buhayra/preprocessing/occurrence_50W_10S.tif']

with fiona.open('/home/delgado/proj/buhayra/preprocessing/semiarido.gpkg','r') as fio:
    semiarido=shape(next(iter(fio))['geometry'])

# open, crop, and sieve
for path_i in jrc_paths:
    with rasterio.open(path_i,'r') as src:
        out_image, out_transform = mask(src,semiarido,all_touched=True,crop=True)
        out_meta = src.meta
    out_image[np.where(out_image>1)]=1
    raster = out_image[0]
    sieved = sieve(raster, 10, out=np.zeros(raster.shape, raster.dtype))
    with rasterio.open(path_i[:-4]+'_bin_sieved.tif','w',driver='GTiff',height=raster.shape[0],width=raster.shape[1],count=1,dtype=rasterio.ubyte,transform=out_transform) as dsout:
        dsout.write(sieved.astype(rasterio.ubyte),1)

# open, merge, and save
src=list()
for path_i in jrc_paths:
    src.append(rasterio.open(path_i[:-4]+'_bin_sieved.tif','r'))

out_rast,out_transform = merge(src,indexes=1)

for i in src:
    i.close()

out_raster = out_rast[0]

with rasterio.open('/home/delgado/proj/buhayra/preprocessing/occurrence_semiarido_bin_sieved.tif','w',driver='GTiff',height=out_raster.shape[0],width=out_raster.shape[1],count=1,dtype=rasterio.ubyte,transform=out_transform) as dsout:
    dsout.write(out_raster.astype(rasterio.ubyte),1)


# burn river masks with gdal
'gdal_rasterize -at -burn 0 ~/proj/buhayra/preprocessing/mask_rivers.gpkg /home/delgado/proj/buhayra/preprocessing/occurrence_40W_0N_burned.tif'

# polygonize
'gdal_polygonize.py  ~/proj/buhayra/preprocessing/occurrence_40W_0N_burned.tif -f GPKG ~/proj/buhayra/preprocessing/wm_40W_0N.gpkg'

# merge and clean feature collections

wms=['/home/delgado/proj/buhayra/preprocessing/wm_50W_0N.gpkg',
    '/home/delgado/proj/buhayra/preprocessing/wm_50W_10S.gpkg',
    '/home/delgado/proj/buhayra/preprocessing/wm_40W_10S.gpkg',
    '/home/delgado/proj/buhayra/preprocessing/wm_40W_0N.gpkg']

ref_path = '/home/delgado/proj/buhayra/preprocessing/jrc_ref.gpkg'

featcoll = list()
id=0
for wm_path in wms:
    with fiona.open(wm_path,'r') as fio:
        for feat in iter(fio):
            if feat['properties']['DN']==1:
                props={}
                id=id+1
                props['id']=id
                featcoll.append(geojson.Feature(geometry=feat['geometry'],properties=props))
gj=geojson.FeatureCollection(featcoll)

with open(ref_path[:-4]+'geojson', 'w') as outfile:
      geojson.dump(gj, outfile)

# insert into postgres
