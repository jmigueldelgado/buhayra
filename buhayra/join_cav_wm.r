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

yes=st_is_within_distance(cav,wm,dist=300,sparse=TRUE)
yes
st_crs(cav)

st_write(wm,"/home/delgado/funceme.gpkg")
st_write(cav,"/home/delgado/res_meta.gpkg")



for( i in seq(1,length(yes))
{
    cav


}

wm[12555,]
