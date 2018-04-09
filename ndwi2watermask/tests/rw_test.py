import rasterio
import numpy as np
dataset = rasterio.open('/home/delgado/Documents/tmp/tes.tif')

band=dataset.read(1)
band_int=band.astype('int16')
band_int

with rasterio.open('/home/delgado/Documents/tmp/tes_out.tif', 'w',driver='GTiff',height=band_int.shape[0], width=band_int.shape[1],count=1,dtype=np.int16) as dst:
    dst.write(band_int, 1)


with rasterio.open('/home/delgado/Documents/tmp/tes_out.tif', 'w',driver='GTiff',height=band.shape[0], width=band.shape[1],count=1,dtype=np.float32) as dst:
    dst.write(band, 1)
