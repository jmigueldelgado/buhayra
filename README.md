# Buhayra

Buhayra (from al-buhayra) is a prototype application aiming at obtaining **water extent of small reservoirs** in semi-arid regions from satellite data in **real-time**. It collects, filters and processes weekly reservoir extents from Sentinel-1 for northeast Brazil and stores this geo-referenced information in a structured data model. This work has been funded by the German Research Foundation [DFG](http://gepris.dfg.de/gepris/projekt/266418622) and runs on the compute server for high performance computing of [ZIM - University of Potsdam](http://www.uni-potsdam.de/de/zim/angebote-loesungen/hpc.html)

## Before you start...

Read about configurations and setup on the [wiki](https://github.com/jmigueldelgado/buhayra/wiki) and create and configure your location file accordingly (in `buhayra/parameters/location.yml`).

The scripts are suited to work on a PBS cluster or at least a dedicated machine with large RAM. There is a crontab that schedules the jobs to run once a week or more often. Although there are [conda environment files](https://conda.io/docs/user-guide/tasks/manage-environments.html#sharing-an-environment) to go with this repo, some libraries are quite machine specific and the currently used environments evolve a lot due to the experimental nature of this repo. Please contact me in case youi want to use any of this.

## What it does

In short, the following steps are done sequentially:

- query the [Copernicus Open Access Hub](https://scihub.copernicus.eu/) for Sentinel-1 and scenes ingested in the past 7 days. Download scenes.

- calibrate, speckle-filter, correct geometry with [snappy](http://step.esa.int/main/toolboxes/snap/) (for SAR data)

- subset based on a [global surface water database](https://global-surface-water.appspot.com/faq) from JRC

- apply [minimum error thresholding](https://www.sciencedirect.com/science/article/abs/pii/0031320386900300)

- polygonize and insert into PostGIS (with the amazing [GDAL](https://gdal.org/))

## Visualization is being provided by a demo [dashboard under development](http://seca-vista.geo.uni-potsdam.de:3838/buhayra-app/).

![example output](https://raw.githubusercontent.com/jmigueldelgado/buhayra/master/documents/screenshot.png)

An evaluation of the results is given by [valbuhayra](https://github.com/jmigueldelgado/valbuhayra)

## In progress:

- combine the water extent collection with bathymetric survey from TanDEM-X

## Some of our references

We were at ESAs [_mapping water bodies from space 2nd conference_](http://mwbs2018.esa.int/) in Frascati (Rome), and at the [_World Water Forum_](http://www.worldwaterforum8.org/) in Brasília 2018.

[Shuping's talk](documents/presentation167.pdf) and [Martin's poster](documents/poster_08.pdf) in Frascati. [My talk](documents/wwf2018.pdf) in Brasília.
