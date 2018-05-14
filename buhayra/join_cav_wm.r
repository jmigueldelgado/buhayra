library(sf)
library(dplyr)
library(readr)
wm=st_read("./buhayra/auxdata/funceme.geojson") %>%
  st_set_crs(32724)

meta=read_csv("./buhayra/auxdata/reservoir_tbl.meta")

cav=read_csv("./buhayra/auxdata/reservoir_tbl.meta") %>%
  filter(is.na(latitude)==FALSE & is.na(longitude)==FALSE) %>%
  st_as_sf(coords=c("longitude","latitude")) %>%
  st_set_crs(4326) %>%
  st_transform(32724)

yes=st_within(cav,wm,sparse=TRUE)

wm[12555,]
