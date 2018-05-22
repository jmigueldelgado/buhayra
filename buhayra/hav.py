import rasterio as rio
import fiona as fio
import fiona.transform
import rasterio.mask
from matplotlib.pyplot import imshow
from shapely.geometry import shape, mapping,Polygon
#import geojson


fname="/home/delgado/SESAM/sesam_data/DFG_Erkenntnis_Transfer/tdx/DEMs/dfd2_506518124_sum_dem_20151014_4x4_geoc_F.tif"
dataset = rio.open(fname)
db=dataset.bounds
dembb=Polygon([[db[0],db[1]], [db[0],db[3]], [db[2],db[3]], [db[2],db[1]]])
#dem = dataset.read(1)

# with fiona
m="/home/delgado/Documents/S1A_IW_GRDH_1SDV_20180422T081723_20180422T081748_021577_0252FF_65E0_x1000_y0_watermask_simplified.geojson"
MASKS=fio.open(m)
mb=MASKS.bounds

tmp=list(fiona.transform.transform(MASKS.crs['init'],dataset.crs['init'],[mb[0]],[mb[1]]))
ll=[tmp[0][0],tmp[1][0]]
tmp=list(fiona.transform.transform(MASKS.crs['init'],dataset.crs['init'],[mb[0]],[mb[3]]))
lu=[tmp[0][0],tmp[1][0]]
tmp=list(fiona.transform.transform(MASKS.crs['init'],dataset.crs['init'],[mb[2]],[mb[3]]))
ru=[tmp[0][0],tmp[1][0]]
tmp=list(fiona.transform.transform(MASKS.crs['init'],dataset.crs['init'],[mb[2]],[mb[1]]))
rl=[tmp[0][0],tmp[1][0]]

maskbb=Polygon([ll,lu,ru,rl])

if maskbb.touches(dembb):


    #elem=MASKS[101]

    for elem in MASKS:
        geom=fiona.transform.transform_geom(MASKS.crs['init'],dataset.crs['init'],elem['geometry'])
        newgeom=shape(geom)

        if newgeom.within(dembb):
            ### the mask has to be a list of geojson!
            print(elem['properties'])


            band, out_transform =rio.mask.mask(dataset,,all_touched=True,crop=True)


imshow(band)

band.max()
band.min()
band[band<300]=300
