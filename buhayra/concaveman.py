import json
import os
from rpy2.robjects.packages import importr
import rpy2.robjects as robjects
from shapely.geometry import mapping, shape

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
        polygon = selected_pts %>% concaveman(.,concavity=1.5) %>% st_zm %>% rename(geometry=polygons)
        return(polygon)
        }''')

    # read geometry object from file
    gdf=sf.st_read(os.path.join(path,geom_file))
    # define function
    r_pts2concave = robjects.r['pts2concave']
    # draw concave hull around points
    gdf_concave = r_pts2concave(gdf)
    # dump json string
    r_gj_string=geojsonsf.sf_geojson(gdf_concave)
    # return dictionary
    return shape(json.loads(r_gj_string[0]))
