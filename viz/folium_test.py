# from here: https://github.com/python-visualization/folium/blob/master/examples/WMS_and_WMTS.ipynb

import os
import folium

print(folium.__version__)
m = folium.Map(location=[-5, -38],zoom_start=8)

folium.raster_layers.WmsTileLayer(url='http://141.89.96.184/latestwms?',layers='watermask',name='buhayra',version='1.3.0',fmt='image/png',transparent=True,srs='EPSG:4326',bbox='-2.8125,-45,0,-42.1875').add_to(m)
folium.LayerControl().add_to(m)

m.save(os.path.join('viz', 'buhayra.html'))
