require(sf)
require(dplyr)
library(lubridate)
library(reshape2)
orson=TRUE
if(orson)
{
    scratch="/mnt/scratch/martinsd"
} else
{
    scratch="/home/delgado/scratch"
}

join_ids_with_feats <- function(ids,psimpl) {
    out <- tryCatch(
        {
            # Just to highlight: if you want to use more than one
            # R expression in the "try" part then you'll have to
            # use curly brackets.
            # 'tryCatch()' will return the last evaluated expression
            # in case the "try" part was completed successfully

            message("This is the 'try' part")

            pfilter <- left_join(ids,psimpl) %>%
                st_as_sf %>%
                group_by(id_cogerh) %>%
                summarize(source_id=as.integer(first(source_id)),ingestion_time=first(ingestion_time),area=sum(area)) %>%
                st_transform(crs=4326) ## back to latlong

            # The return value of `readLines()` is the actual value
            # that will be returned in case there is no condition
            # (e.g. warning or error).
            # You don't need to state the return value via `return()` as code
            # in the "try" part is not wrapped insided a function (unlike that
            # for the condition handlers for warnings and error below)
            return(pfilter)
        },
        error=function(cond) {
            message("Problem with join. Possibly a topological error.")
            message("Here's the original error message:")
            message(cond)
            # Choose a return value in case of error
            return(0)
        },
        warning=function(cond) {
            message("There was a warning:")
            message("Here's the original warning message:")
            message(cond)
            # Choose a return value in case of warning
            return(pfilter)
        },
        finally={
        # NOTE:
        # Here goes everything that should be executed at the end,
        # regardless of success or error.
        # If you want more than one expression to be executed, then you
        # need to wrap them in curly brackets ({...}); otherwise you could
        # just have written 'finally=<expression>'
#            message(paste("Processed URL:", url))
#            message("Some other message at the end")
        }
    )
    return(out)
}



wmIn <- paste0(scratch,"/watermasks")

flist <- list.files(wmIn,pattern="_watermask.gml$")

cogerh <- st_read("./auxdata/cogerh.geojson") %>%
    as_tibble %>%
    st_as_sf() %>%
    st_set_crs(32724)
### read, remove small parts, remove DN==0 (land), simplify with threshold between 10 and 15 preserving topology. It should reduce size of vector by a factor of at least 3.
for(f in flist)
{
    cat("\nChecking file:\n",f,"\n")
    fname=substr(f,1,nchar(f)-4)
### if file has't been processed yet:
    if(!file.exists(paste0(wmIn,"/",fname,"_simplified.geojson")))
    {
        cat("\nNot yet processed, processing ....\n")

        if(substr(f,1,2)=="S1")
          {
            p <- st_read(paste0(wmIn,"/",f)) %>%
            as_tibble %>%
            st_as_sf %>%
            st_set_crs(4326) %>%
            st_transform(crs=32724) %>%
            filter(DN>0)
          }
        if(substr(f,1,2)=="S2")
            {
              p <- st_read(paste0(wmIn,"/",f)) %>%
              as_tibble %>%
              st_as_sf %>%
              st_set_crs(32724) %>%
              filter(DN>0)
            }

        if(nrow(p)>0)
        {
            p <- p %>%
                mutate(id_in_scene=row_number(),area=st_area(.)) %>%
                filter(as.numeric(area)>1000) %>%
                select(-fid,-DN)
            if(strsplit(f,"_")[[1]][1]=="S1A")
                {
                  cat("simplifying S1A")
                  p = p %>%
                 mutate(ingestion_time=strsplit(f,"_")[[1]][5] %>% ymd_hms(),source_id=as.integer(1))
               }
            if(strsplit(f,"_")[[1]][1] %in% c("S2A","S2B","S2C") )
               {
                 cat("simplifying S2A")
                 p = p %>%
                 mutate(ingestion_time=strsplit(f,"_")[[1]][3] %>% ymd_hms(),source_id=as.integer(2))
               }

            psimpl <- st_simplify(p,preserveTopology=TRUE,dTolerance=11)
            ints <- st_intersects(psimpl,cogerh,sparse=TRUE) %>% unclass(.) %>% melt(.)

            ids=data_frame(id_cogerh=cogerh$id[ints$value],id_in_scene=psimpl$id_in_scene[ints$L1])

                                        #pfilter <- left_join(ids,psimpl) %>% st_as_sf %>% split(.$id_cogerh) %>% lapply(st_union) %>% do.call(c,.) %>% st_cast
            if(nrow(ids)>0)
            {
              pfilter=join_ids_with_feats(ids,psimpl)
              if(pfilter!=0)
              {
                st_write(pfilter,paste0(wmIn,"/",fname,"_simplified.geojson"),driver="GeoJSON")
              }

            } else cat("\n\nPolygons matching the COGERH watermask were not found in ",f,"\n")
        } else cat("\n\n The watermask was not found, check if scene is over the ocean or if there are no water bodies on the scene. \n\n")
    } else cat("\nAlready processed, jumping over simplify and filter ....\n")

### if file has been processed and input file is still stored, remove it
    if(file.exists(paste0(wmIn,"/",f)))
    {
        cat("\nDeleting:\n",paste0(wmIn,"/",f))
        try(file.remove(paste0(wmIn,"/",fname,".gml")),silent=TRUE)
        try(file.remove(paste0(wmIn,"/",fname,".xsd")),silent=TRUE)
    }
}
