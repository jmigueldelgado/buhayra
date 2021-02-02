#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)

# test if there is at least one argument: if not, return an error
if (length(args)<2) {
  stop("Two arguments must be supplied: the absolute path and the input file.\n", call.=FALSE)
}

library(dplyr)
library(sf)
library(concaveman)

edges_pts=st_read(file.path(args[1],args[2])) %>% st_transform(32724)
selected_pts = edges_pts %>% group_by(id) %>% tally %>% filter(n==max(n))
polygon = selected_pts %>% concaveman(.,concavity=1.5) %>% st_transform(4326)

fname=paste0(substr(args[2],1,nchar(args[2])-8),'_concave_hull.geojson')

st_write(polygon,dsn=file.path(args[1],fname),driver='GeoJSON')

