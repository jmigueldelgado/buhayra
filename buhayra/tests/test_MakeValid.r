library(sf)
library(lwgeom)
pols=st_read("/home/delgado/Documents/S1A_IW_GRDH_1SDV_20180422T081723_20180422T081748_021577_0252FF_65E0_x1000_y8425_watermask_simplified.geojson")



pols2=st_read("/home/delgado/Documents/latest.geojson")
pols2=st_read("/home/delgado/Documents/id_cogerh_1.geojson")

plot(pols2)


p1=st_as_sfc("MULTIPOLYGON(((-38.98700715127529 -7.006288515707424, -38.98700715127529 -7.006737673349483, -38.9866478251617 -7.006737673349472, -38.9866478251617 -7.00628851570742, -38.98700715127529 -7.006288515707424)))")

p1
plot(p1)
sum(st_is_valid(pols))
nrow(pols)




pols_val=st_make_valid(pols)

val=st_is_valid(pols_val)
sum(val)==length(val)
st_crs(pols)
