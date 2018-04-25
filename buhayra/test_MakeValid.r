library(sf)
library(lwgeom)
pols=st_read("/home/delgado/Documents/S1A_IW_GRDH_1SDV_20180422T081723_20180422T081748_021577_0252FF_65E0_x1000_y8425_watermask_simplified.geojson")

valid=st_is_valid(pols)

polsval=pols[valid,]

head(polsval)

sf_extSoftVersion()["lwgeom"]

pols_val=st_make_valid(pols)

val=st_is_valid(pols_val)
sum(val)==length(val)
st_crs(pols)


pols2=st_read("/home/delgado/Documents/S2B_MSIL1C_20180310T130239_N0206_R095_T24MXU_20180310T143948_watermask_simplified.geojson")
