# from here: https://github.com/python-visualization/folium/blob/master/examples/WMS_and_WMTS.ipynb

import os
import folium
from folium.plugins import FastMarkerCluster, MarkerCluster
# import fiona
from shapely.geometry import mapping, Polygon, shape
import geojson
import buhayra.defAggregations as aggr
#
#
# aggr.ogr_getLatestIngestionTime()

def make_html():
    m = folium.Map(location=[ 38.2,-8],zoom_start=8)

    folium.raster_layers.WmsTileLayer(url='http://141.89.96.184/latestwms?',
        layers='watermask-sib',
        name='SAR Watermasks',
        version='1.3.0',
        fmt='image/png',
        transparent=True,
        srs='EPSG:4326',
        bbox='37.0,-10,40,-5.0').add_to(m)

    folium.raster_layers.WmsTileLayer(url='http://141.89.96.184/latestwms?',
        layers='JRC-Global-Water-Bodies-sib',
        name='JRC Static Water Bodies',
        version='1.3.0',
        fmt='image/png',
        transparent=True,
        srs='EPSG:4326',
        bbox='37.0,-10,40,-5.0').add_to(m)

    # folium.GeoJson('/home/delgado/domain_ll_lines.geojson',name='TanDEM-X available and processed DEMs',tooltip=folium.features.GeoJsonTooltip(fields=['file'],aliases=['File Name'],labels=True,localize=True,sticky=True)).add_to(m)



    folium.LayerControl().add_to(m)

    m.save(os.path.join('/home','delgado','proj','buhayra','viz', 'reserv-sib.html'))
