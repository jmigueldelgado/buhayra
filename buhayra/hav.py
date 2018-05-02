import rasterio as rio
import fiona as fio
import fiona.transform
import rasterio.mask
from matplotlib.pyplot import imshow
#import geojson


fname="/home/delgado/SESAM/sesam_data/DFG_Erkenntnis_Transfer/tdx/DEMs/dfd2_506518124_sum_dem_20151014_4x4_geoc_F.tif"
dataset = rio.open(fname)
#dem = dataset.read(1)

# with fiona
m="/home/delgado/Documents/S1A_IW_GRDH_1SDV_20180422T081723_20180422T081748_021577_0252FF_65E0_x1000_y0_watermask_simplified.geojson"
MASKS=fio.open(m)

#with geojson
#with open(m) as f:
#    MASKS=geojson.load(f)

newMASKS=list()
geom=MASKS[1]
for geom in MASKS:
    newgeom=geom
    newgeom['geometry']=fiona.transform.transform_geom(MASKS.crs['init'],dataset.crs['init'],geom['geometry'])
    newgeom['geometry']
    newMASKS.append(newgeom)

newMASKS[40]


dataset.bounds
newMASKS
newMASKS[1]
newMASKS=type(newMASKS)
newMASKS[101]

### the mask has to be a list of geojson!
band, out_transform =rio.mask.mask(dataset,[newMASKS[101]],all_touched=True,crop=True)
imshow(band)

band.max()
band.min()
band[band<300]=300
