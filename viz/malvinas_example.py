from bokeh.io import show, output_notebook, output_file
from bokeh.models import (GeoJSONDataSource,HoverTool,LinearColorMapper)
from bokeh.plotting import figure
from bokeh.palettes import Viridis6

with open(r'./viz/malvinas.geojson', 'r') as f:
    geo_source = GeoJSONDataSource(geojson=f.read())


color_mapper = LinearColorMapper(palette=Viridis6)

TOOLS = "pan,wheel_zoom,box_zoom,reset,hover,save"

p = figure(title="Argentina", tools=TOOLS, x_axis_location=None, y_axis_location=None, width=500, height=300)
p.grid.grid_line_color = None

p.patches('xs', 'ys', fill_alpha=0.7, fill_color={'field': 'objectid', 'transform': color_mapper},
          line_color='white', line_width=0.5, source=geo_source)


hover = p.select_one(HoverTool)
hover.point_policy = "follow_mouse"
hover.tooltips = [("Provincia:", "@provincia")]

output_file("PBIar.html", title="Testing islands in bokeh")

show(p)
