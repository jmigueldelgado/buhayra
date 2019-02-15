# from here: https://github.com/python-visualization/folium/blob/master/examples/WMS_and_WMTS.ipynb

import os
import folium
from folium.plugins import FastMarkerCluster, MarkerCluster
# import fiona
from buhayra.getpaths import *
from shapely.geometry import mapping, Polygon, shape
import geojson
import buhayra.defAggregations as aggr
#
#
# aggr.ogr_getLatestIngestionTime()

def make_html():
    m = folium.Map(location=[-3.9058, -39.4626],zoom_start=10)
    # folium.map.Icon(color='green',)
    # folium.GeoJson('./buhayra/auxdata/unidades-hidrograficas-CE.geojson',name='geojson',tooltip=folium.features.GeoJsonTooltip(fields=['UHE_NM'],aliases=['unidade hidrográfica'],labels=True,localize=True)).add_to(m)
    # mkrs=folium.GeoJson('./viz/latest-markers.geojson',name='geojson',tooltip=folium.features.GeoJsonTooltip(fields=['ingestion_time'],aliases=['ingestion time'],labels=True,localize=True,sticky=True))

    marker_cluster = MarkerCluster(
        name='Reservoir Area, Ingestion Time and Available DEMs',
        overlay=True,
        control=True,
        # icon_create_function=None
    )

    folium.raster_layers.WmsTileLayer(url='http://141.89.96.184/latestwms?',
        layers='watermask',
        name='SAR Watermasks',
        version='1.3.0',
        fmt='image/png',
        transparent=True,
        srs='EPSG:4326',
        bbox='-2.8125,-45,0,-42.1875').add_to(m)

    folium.raster_layers.WmsTileLayer(url='http://141.89.96.184/latestwms?',
        layers='JRC-Global-Water-Bodies',
        name='JRC Static Water Bodies',
        version='1.3.0',
        fmt='image/png',
        transparent=True,
        srs='EPSG:4326',
        bbox='-2.8125,-45,0,-42.1875').add_to(m)

    folium.GeoJson('/home/delgado/domain_ll_lines.geojson',name='TanDEM-X available and processed DEMs',tooltip=folium.features.GeoJsonTooltip(fields=['file'],aliases=['File Name'],labels=True,localize=True,sticky=True)).add_to(m)



    folium.LayerControl().add_to(m)

    m.save(os.path.join(home['home'], 'reserv+DEMs.html'))
