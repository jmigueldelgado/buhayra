# connect to the API
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date, datetime, timedelta
import sys
import os
from buhayra.getpaths import *
import logging
from bs4 import BeautifulSoup
import requests
import urllib


def list_url(url, ext=''):
    page = requests.get(url).text
    # print(page)
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

def getscenes():
    logger = logging.getLogger('root')

    api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')
    logging.info(api.api_url)
    # download single scene by known product id
    #api.download(<product_id>)
    t0 = datetime.now() - timedelta(days=7)
    tf = datetime.now()

    # first get orbit files
    t=tf
    eof_urls=list()
    while t>=t0:
        url=orbits_url+datetime.strftime(t,'%Y/%m/%d')+'/'
        for file in list_url(url, 'EOF'):
            urllib.request.urlopen(file)
            eof_urls.append(file)
            # print(file)
        t=t-timedelta(days=1)



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

def getscenes_past(nmonths):
    logger = logging.getLogger('root')

    api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')
    logging.info(api.api_url)
    # download single scene by known product id
    #api.download(<product_id>)
    t0 = datetime(2018,1,1,0,0,0)
    tf = t0 + timedelta(days=nmonths*30)

    # search by polygon, time, and SciHub query keywords
    footprint = geojson_to_wkt(read_geojson(home['parameters'] + '/extent_ce.geojson'))
    # products_s2a = api.query(footprint,
    #                     date=(
    #                         date(t0.year,t0.month,t0.day),
    #                         date(tf.year,tf.month,tf.day)
    #                         ),
    #                         platformname='Sentinel-2',
    #                         cloudcoverpercentage = (0, 20))
    #
    #
    # # download all results from the search
    # #s2aIn = '/home/delgado/Documents/tmp' # in case you are just testing
    # for item in products_s2a:
    #     logging.info(products_s2a[item]['title'])

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
    # api.download_all(products_s2a,directory_path=s2aIn)

def getscenes_test_dataset():
    logger = logging.getLogger('root')

    api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')
    logging.info(api.api_url)
    # download single scene by known product id
    #api.download(<product_id>)
    t0 = datetime.now() - timedelta(months=8)
    tf = datetime.now()
    # search by polygon, time, and SciHub query keywords
    footprint = geojson_to_wkt(read_geojson(home['parameters'] + '/madalena.geojson'))

    products_s1a = api.query(footprint,
                         date=(
                             date(t0.year,t0.month,t0.day),
                             date(tf.year,tf.month,tf.day)
                         ),
                         producttype="GRD",
                         platformname='Sentinel-1')
    for item in products_s1a:
        logging.info(products_s1a[item]['title'])

    tests1In = scratch + "/test_dataset/s1a_scenes/in"

        # download all results from the search
    api.download_all(products_s1a,directory_path=tests1In)
