library(sf)
library(dplyr)

wm=st_read('/home/delgado/proj/buhayra/buhayra/auxdata/wm_utm.gpkg')

head(wm)

nr=nrow(wm)
wm$id=seq(1,nr)
wm$region='Ceará'
wm=subset(wm,select=-water)
head(wm)
wm_simplf=st_simplify(wm,preserveTopology=TRUE,dTolerance=11)

st_write(wm_simplf,'/home/delgado/proj/buhayra/buhayra/auxdata/wm_utm_simplf.gpkg')
