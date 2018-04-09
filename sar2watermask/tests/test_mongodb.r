library(sf)
library(mongolite)
library(ggplot2)
library(dplyr)
library(geojsonio)
library(lubridate)
library(jsonlite)
                                        #library(geosphere)
#library(rgeos)

wm_in <- "~/scratch/watermasks/"

flist <- list.files(wm_in,pattern="simplified.gml")

f <- flist[1]

### read, remove small parts, remove DN==0 (land), simplify with threshold between 10 and 15 preserving topology. It should reduce size of vector by a factor of at least 3.

p <- st_read(paste0(wm_in,f)) %>%
    as_tibble %>%
    st_as_sf %>%
    mutate(ingestion_time=ymd_hms(ingestion_time,tz="UTC"))

sfPl <- p[1,]
tbl <- sfPl
st_geometry(tbl) <- NULL
sfcPl <- st_geometry(p)[1]
sfgPl <- st_geometry(p)[[1]]

tb <- toJSON(tbl)
g <- geojson_json(sfPl)

class(sfPl)
class(sfcPl)
class(sfgPl)


m <- mongo(collection = "test",  db = "test", url = "mongodb://localhost")

m$insert(tbl)
m$update(toJSON(select(tbl,fid)),geojson_json(sfPl))

m$count()
m$count('{"features.properties.id_cogerh":6114}')
m$count('{ "features.properties.ingestion_time" : { "$gte" : ISODate("2017/10/05T00:00:00.00Z") } }')
m$find('{ "id_cogerh" : { "$lte" : 6114 } }')
m$count('{ "ingestion_time" : { "$gte" : ISODate("2017/10/05T00:00:00Z") } }')
m$count('{ "features.properties.id_cogerh" : { "$lte" : 6114 } }')

m$find(select(tbl,fid))
m$find('{"fid":"S1A_IW_GRDH_1SDV_20171105T081725_20171105T081750_019127_0205D1_D44E_x12812_y0_watermask.gml_simplified.0"}')
m$count(toJSON(select(tbl,fid)))
