# from here: https://github.com/python-visualization/folium/blob/master/examples/WMS_and_WMTS.ipynb

import os
import folium
from folium.plugins import FastMarkerCluster, MarkerCluster
import fiona
from buhayra.getpaths import *
from shapely.geometry import mapping, Polygon, shape
import geojson
import buhayra.defAggregations as aggr
#
#
# aggr.ogr_getLatestIngestionTime()


def update_metadata():
    bbox = Polygon([[-40.20,-3.0], [-38.3,-3.0], [-38.3,-4.50], [-40.20,-4.50]])
    path_to_geojson = aggr.ogr_getLatestIngestionTime()
    with fiona.open(path_to_geojson,'r') as latest:
        feats=list()

        for feat in latest:
            if feat['geometry'] is None or not shape(feat['geometry']).within(bbox):
                continue
            pnt = geojson.Point()
            pnt['coordinates']=feat['geometry']['coordinates']
            feats.append(geojson.Feature(geometry=pnt,properties=feat['properties']))

    return geojson.FeatureCollection(feats)

def make_html():
    m = folium.Map(location=[-3.9058, -39.4626],zoom_start=10)
    # folium.map.Icon(color='green',)
    # folium.GeoJson('./buhayra/auxdata/unidades-hidrograficas-CE.geojson',name='geojson',tooltip=folium.features.GeoJsonTooltip(fields=['UHE_NM'],aliases=['unidade hidrográfica'],labels=True,localize=True)).add_to(m)
    # mkrs=folium.GeoJson('./viz/latest-markers.geojson',name='geojson',tooltip=folium.features.GeoJsonTooltip(fields=['ingestion_time'],aliases=['ingestion time'],labels=True,localize=True,sticky=True))

    marker_cluster = MarkerCluster(
        name='Reservoir Area and Ingestion Time',
        overlay=True,
        control=True,
        # icon_create_function=None
    )
    featcoll = update_metadata()
    for feat in featcoll['features']:

        location =feat['geometry']['coordinates'][1],feat['geometry']['coordinates'][0]
        marker = folium.Marker(location=location,icon=folium.map.Icon('fa-angle-down'))
        popup = ('id: {:6d}'.format( feat['properties']['id_jrc'])+
            '<br>Area: {:.2f} ha'.format(feat['properties']['area']/10000)+
            '<br>Ingestion Time: {}'.format(feat['properties']['ingestion_time']))
        folium.Popup(popup).add_to(marker)
        marker_cluster.add_child(marker)

    marker_cluster.add_to(m)


    # FastMarkerCluster(data=mkrs.data).add_to(m)

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



    folium.LayerControl().add_to(m)

    m.save(os.path.join(home['home'], 'index.html'))
