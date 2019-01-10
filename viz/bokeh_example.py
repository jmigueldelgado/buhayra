
import json
from bokeh.io import show, output_notebook, output_file
from bokeh.models import (GeoJSONDataSource,HoverTool,LinearColorMapper)
from bokeh.plotting import figure
from bokeh.palettes import Viridis6

# with open(r'./viz/reservoir_example.geojson', 'r') as f:
#     geo_source = GeoJSONDataSource(geojson=f.read())

with open('./viz/latest-2-month.geojson') as f:
    data = json.load(f)

data['features'][2]['geometry'] is None
nonones = [item for item in data['features'] if item['geometry'] is not None]

data['features']=nonones
data['features'][0]
# gj=data
# gj['features']=gj['features'][0:2]
geo_source = GeoJSONDataSource(geojson=json.dumps(data))

color_mapper = LinearColorMapper(palette=Viridis6)

TOOLS = "pan,wheel_zoom,box_zoom,reset,hover,save"

p = figure(title="Buhayra", tools=TOOLS, x_axis_location=None, y_axis_location=None, width=1000, height=600)
p.grid.grid_line_color = None

# p.patches('xs', 'ys', fill_alpha=0.7, fill_color={'field': 'id_jrc', 'transform': color_mapper},
#           line_color='white', line_width=0.5, source=geo_source)
p.patches('xs', 'ys', fill_alpha=0.7, fill_color='black',
          line_color='white', line_width=0.5, source=geo_source)


hover = p.select_one(HoverTool)
hover.point_policy = "follow_mouse"
hover.tooltips = [("Reservoir:", "@id_jrc")]

output_file("buhayra.html", title="Testing lakes in bokeh")

show(p)
