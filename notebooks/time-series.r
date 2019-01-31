library(sf)
library(dplyr)

getwd()

dataset = st_read('test_data/time-series-2019-01-31.geojson')


head(dataset) %>% plot
