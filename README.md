# Buhayra

Buhayra (from al-buhayra) is a prototype application aiming at obtaining water extent of small reservoirs in semi-arid regions from satellite data. It collects, filters and processes sentinel-1 scenes for northeast Brazil and stores the water extent in a structured data model. This work has been funded by the German Research Foundation [DFG](http://gepris.dfg.de/gepris/projekt/266418622) and runs on the compute server for high performance computing of [ZIM - University of Potsdam](http://www.uni-potsdam.de/de/zim/angebote-loesungen/hpc.html)

<!-- ## [sar2watermask](https://github.com/jmigueldelgado/buhayra/tree/master/sar2watermask)

This repository deals with Sentinel-1

## [ndwi2watermask](https://github.com/jmigueldelgado/buhayra/tree/master/ndwi2watermask)

This repository deals with Sentinel-2 -->

## Before you start...

Read about configurations and setup on the [wiki](https://github.com/jmigueldelgado/buhayra/wiki)

The scripts are suited to work on a PBS cluster. There is a crontab that schedules the jobs to run once a week or more often. Although there are [conda environment files](https://conda.io/docs/user-guide/tasks/manage-environments.html#sharing-an-environment) to go with this repo, this is by definition all very machine specific!

## What it does

In short, the following steps are done sequentially:

- query the [Copernicus Open Access Hub](https://scihub.copernicus.eu/) for sentinel-1 and sentinel-2 scenes ingested in the past 7 days. Download scenes

- extract a watermask with [snappy](http://step.esa.int/main/toolboxes/snap/) (for SAR data)

- polygonize watermask using [gdal](https://pypi.python.org/pypi/GDAL/)

- simplify polygons (with [R's sf](https://github.com/r-spatial/sf/)) and match their IDs with the [FUNCEME](https://www.funceme.br/) dataset

- insert into mongodb and PostGIS (still running these two in parallel, not sure which one will survive)

## Visualization is being provided by a dedicated [website in development](http://141.89.96.184/) and by the drought forecast tool [seca-vista](http://seca-vista.geo.uni-potsdam.de/).

![example output](https://raw.githubusercontent.com/jmigueldelgado/buhayra/master/documents/screenshot.png)

## Preliminary Results

Preliminary results can be seen [here](http://141.89.96.184)

An evaluation of the results is given by [valbuhayra](https://github.com/jmigueldelgado/valbuhayra)


## In progress:
- combine the water extent collection with bathymetric survey from TanDEM-X

## Some references

We were at ESAs [_mapping water bodies from space 2nd conference_](http://mwbs2018.esa.int/) in Frascati (Rome), and at the [_World Water Forum_](http://www.worldwaterforum8.org/) in Brasília 2018.

[Shuping's talk](documents/presentation167.pdf) and [Martin's poster](documents/poster_08.pdf) in Frascati. [My talk](documents/wwf2018.pdf) in Brasília.
