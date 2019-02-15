from shapely.geometry import mapping, Polygon, shape
from shapely.ops import cascaded_union, transform
import os
import pyproj
import fiona
import rasterio
from buhayra.getpaths import *
from rasterio.features import sieve, shapes, rasterize
from rasterio.mask import mask
from rasterio.merge import merge
import numpy as np
import geojson


jrc_paths = ['/home/delgado/proj/buhayra/preprocessing/occurrence_10W_40N.tif']
    # '/home/delgado/proj/buhayra/preprocessing/occurrence_10W_50N.tif']



with fiona.open('/home/delgado/proj/buhayra/preprocessing/alentejo.gpkg','r') as fio:
    alentejo=shape(next(iter(fio))['geometry'])


# open, crop, and sieve
for path_i in jrc_paths:
    with rasterio.open(path_i,'r') as src:
        out_image, out_transform = mask(src,[alentejo],all_touched=True,crop=True)
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
'cp occurrence_10W_40N_bin_sieved.tif occurrence_10W_40N_burned.tif'
'gdal_rasterize -at -burn 0 ~/proj/buhayra/preprocessing/sib_mask_rivers.gpkg /home/delgado/proj/buhayra/preprocessing/occurrence_10W_40N_burned.tif'


# polygonize
'gdal_polygonize.py  ~/proj/buhayra/preprocessing/occurrence_10W_40N_burned.tif -f GPKG ~/proj/buhayra/preprocessing/wm_10W_40N.gpkg'

# merge and clean feature collections

wms=['/home/delgado/proj/buhayra/preprocessing/wm_10W_40N.gpkg']

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
