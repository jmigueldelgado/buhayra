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
from buhayra.location import *


def get_s1_orbits(t0,tf):
    def list_url(url, ext=''):
        page = requests.get(url).text
        # print(page)
        soup = BeautifulSoup(page, 'html.parser')
        return [url + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

    logger = logging.getLogger('root')
    # first get orbit files
    t=tf
    # eof_urls=list()
    # file_url=list_url(url, 'EOF')[0]
    while t>=t0:
        url=orbits_url+datetime.strftime(t,'%Y/%m/%d')+'/'
        for file_url in list_url(url, 'EOF'):
            fname=file_url.split('/')[-1]
            directory=home['home']+\
                '/.snap/auxdata/Orbits/Sentinel-1/RESORB/'+fname[0:3]+'/'+\
                datetime.strftime(t,'%Y')+\
                '/'+\
                datetime.strftime(t,'%m')+\
                '/'
            if not os.path.isdir(directory):
                logging.info(directory+' not found. Making')
                os.makedirs(directory)
            logging.info('Retrieving '+fname)
            if not os.path.isfile(directory+fname):
                urllib.request.urlretrieve(file_url,directory+fname)
        t=t-timedelta(days=1)


def get_scenes():
    logger = logging.getLogger('root')

    api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')
    logging.info(api.api_url)
    # download single scene by known product id
    #api.download(<product_id>)
    tf = datetime.now()
    # tf=datetime(2018,1,10)
    t0 = tf - timedelta(days=5)

    # get_s1_orbits(t0,tf)


    # search by polygon, time, and SciHub query keywords
    footprint = geojson_to_wkt(read_geojson(home['parameters'] + '/extent_'+location['region']+'.geojson'))

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
    # already downloaded files are skipped
    api.download_all(products_s1a,directory_path=sarIn)

def get_past_scenes(Y,M):
    logger = logging.getLogger('root')

    api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')

    logging.info(api.api_url)

    t0 = datetime(Y,M,1,0,0,0)
    tf = t0 + timedelta(days=30)

    # get_s1_orbits(t0,tf)


    # search by polygon, time, and SciHub query keywords
    footprint = geojson_to_wkt(read_geojson(home['parameters'] + '/extent_'+location['region']+'.geojson'))

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
    # already downloaded files are skipped
    api.download_all(products_s1a,directory_path=sarIn)


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

    tests1In = home['scratch'] + "/test_dataset/s1a_scenes/in"

        # download all results from the search
    api.download_all(products_s1a,directory_path=tests1In)
