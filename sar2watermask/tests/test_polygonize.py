
import gdal
#gdal.UseExceptions()

#
#  get raster datasource
#
src_ds = gdal.Open("/home/delgado/scratch/s1a_scenes/out/S1A_IW_GRDH_1SDV_20171105T081725_20171105T081750_019127_0205D1_D44E_Cal_TC_CalCorr.tif" )

if src_ds is None:
    print 'Unable to open %s' % src_filename
    sys.exit(1)

try:
    srcband = src_ds.GetRasterBand(1)
except RuntimeError, e:
    # for example, try GetRasterBand(10)
    print 'Band ( %i ) not found' % band_num
    print e
    sys.exit(1)

dst_layername = "/mnt/scratch/martinsd/s1a_scenes/out/POLYGONIZED_STUFF"
drv = ogr.GetDriverByName("ESRI Shapefile")
dst_ds = drv.CreateDataSource( dst_layername + ".shp" )
dst_layer = dst_ds.CreateLayer(dst_layername, srs = None )

gdal.Polygonize( srcband, None, dst_layer, -1, [], callback=None )
