# sar2watermask

A project for automatic download and processing sentinel-1 SAR files. It calibrates, filters, extracts watermask, writes to GeoTiff, polygonizes and simplifies polygon.

Before you start, read the configuration instructions on the [wiki](https://github.com/jmigueldelgado/sar2watermask/wiki/configuration)

The scripts are suited to work on a PBS cluster. There is a crontab that schedules the jobs to run once a week.

The workflow is as follows:

## Query the [Copernicus Open Access Hub](https://scihub.copernicus.eu/) with `sar2watermask/modules/getRecentScenes.py`

- query sentinel-1 scenes ingested in the past 7 days
- download results

## Extract Watermask with `sar2watermask_cluster.py`

- Subsetting into 4 tiles
- Calibration
- Speckle filtering
- Band Arithmetics 1 (extracting watermask)
- Terrain Correction
- Band Arithmetics 2 (removing interpolation artefacts from terrain correction)
- write results to geotiff

## Polygonize raster with `polygonize.py`
- use GDAL for polygonizing looping over all files

## Simplify polygons based on given dataset of maximum reservoir extent
- match polygons with COGERH watermask and attribute `id`s
- use `st_simplify` from package _sf_ in _R_ to simplify polygons

## Insert into mongodb
- insert each `id` together with corresponding spatial feature into _mongodb_

## From the webserver query _mongodb_
- aggregate db to obtain latest polygon of each `id`
- aggregate db to obtain time-series of area and volume for each `id`

## Clean up
- remove all raster stored in `s1a_scenes/in` and `s1a_scenes/out`

## To do:
- improve threshold selection with shupings algorithm
- parallel processing
