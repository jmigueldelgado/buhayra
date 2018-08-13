# connect to the API
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date, datetime, timedelta
import sys
import os
from buhayra.getpaths import *
import logging

def getscenes():
    logger = logging.getLogger('root')

    api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')
    logging.info(api.api_url)
    # download single scene by known product id
    #api.download(<product_id>)
    t0 = datetime.now() - timedelta(days=7)
    tf = datetime.now()
    # search by polygon, time, and SciHub query keywords
    footprint = geojson_to_wkt(read_geojson(home['parameters'] + '/extent_ce.geojson'))
    products_s2a = api.query(footprint,
                        date=(
                            date(t0.year,t0.month,t0.day),
                            date(tf.year,tf.month,tf.day)
                            ),
                            platformname='Sentinel-2',
                            cloudcoverpercentage = (0, 20))


    # download all results from the search
    #s2aIn = '/home/delgado/Documents/tmp' # in case you are just testing
    for item in products_s2a:
        logging.info(products_s2a[item]['title'])

    products_s1a = api.query(footprint,
                         date=(
                             date(t0.year,t0.month,t0.day),
                             date(tf.year,tf.month,tf.day)
                         ),
                         producttype="GRD",
                         platformname='Sentinel-1')
    for item in products_s1a:
        logging.info(products_s1a[item]['title'])

        # download all results from the search
    api.download_all(products_s1a,directory_path=sarIn)
    api.download_all(products_s2a,directory_path=s2aIn)
