import json
import os
from rpy2.robjects.packages import importr
import rpy2.robjects as robjects
from shapely.geometry import mapping, shape
from buhayra.getpaths import *
import buhayra.insertPolygons as insert
import buhayra.polygonize as poly
import logging
import sys
import geojson
import datetime
import IPython

def concave_hull(geom_file,path):
    # import R packages
    dplyr = importr('dplyr')
    sf = importr('sf')
    concaveman = importr('concaveman')
    geojsonsf = importr('geojsonsf')

    # define r function for drawing a concave hull around points
    robjects.r('''pts2concave = function(sf_df)
        {
        edges_pts = sf_df %>% st_transform(32724)
        selected_pts = edges_pts %>% group_by(id) %>% tally %>% filter(n==max(n))
        polygon = selected_pts %>% concaveman(.,concavity=1.5) %>% st_zm %>% rename(geometry=polygons) %>% st_transform(4326)
        return(polygon)
        }''')

    # read geometry object from file
    gdf=sf.st_read(os.path.join(path,geom_file),quiet=True)
    # define function
    r_pts2concave = robjects.r['pts2concave']
    # draw concave hull around points
    gdf_concave = r_pts2concave(gdf)
    # dump json string
    r_gj_string=geojsonsf.sf_geojson(gdf_concave)
    # return dictionary
    return shape(json.loads(r_gj_string[0]))



# def concaveman_insert(tiffs,refgeoms):

#     logger = logging.getLogger('root')

#     with open(os.path.join(home['home'],'ogr2ogr.log'), 'a') as o_std, open(os.path.join(home['home'], 'ogr2ogr.err'), 'a') as o_err:
#         ls = list()
#         gj_path = os.path.join(polOut,'watermask-tmp-'+datetime.datetime.today().strftime('%Y-%m-%d_%H%M%S%f')+'.geojson')
#         logger.info('drawing concave hull and saving to '+gj_path)

#         ls = list()

#         for abs_path in tiffs:
#             filename = os.path.split(abs_path)[-1][:-3] + 'geojson'
#             productName='_'.join(filename[:-8].split('_')[:9])
#             #            if os.path.exists(os.path.join(edgeOut,productName,filename[:-8]+'_concave_hull.geojson')) | os.path.exists(os.path.join(edgeOut,productName,filename[:-8]+'_NA_SAR.finished')) | os.path.exists(os.path.join(edgeOut,productName,filename[:-8]+'_empty_geometry.geojson')):
#             if os.path.exists(os.path.join(edgeOut,productName,filename[:-8]+'_NA_SAR.finished')) | os.path.exists(os.path.join(edgeOut,productName,filename[:-8]+'_empty_geometry.geojson')):
#                 continue
# #            IPython.embed()
#             try:
#                 pol = concave_hull(filename,os.path.join(edgeOut,productName))
#             except:
#                 logger.info("Unexpected error: "+ sys.exc_info()[0]+" when opening "+abs_path)
#                 continue
#             pol_in_jrc, intersection_area = poly.select_intersecting_polys(pol,refgeoms,filename)
#             #IPython.embed()
#             dict = poly.prepareDict(pol_in_jrc,filename,999,intersection_area)
#             ls.append(dict)
#             open(os.path.join(edgeOut,productName,filename[:-8]+'_concave_hull.geojson'),'w').close()
#         featcoll = poly.json2geojson(ls)

#         if len(ls)>0:
#             with open(gj_path,'w') as f:
#                 geojson.dump(featcoll,f)

#         insert.insert_into_postgres(gj_path,o_std,o_err)
#         logger.info('finished inserting '+gj_path)
