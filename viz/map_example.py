from bokeh.plotting import figure, show, output_file
from bokeh.tile_providers import STAMEN_TERRAIN_RETINA

epsg3857

output_file("tile.html")

# range bounds supplied in web mercator coordinates
p = figure(x_range=(-2000000, 6000000), y_range=(-1000000, 7000000))#,
           # x_axis_type="mercator", y_axis_type="mercator")
p.add_tile(STAMEN_TERRAIN_RETINA)

show(p)

project = partial(
    pyproj.transform,
    pyproj.Proj(init='epsg:4326'),
    pyproj.Proj(init='epsg:'))
geom_utm=transform(project,geom)
