import ee
ee.Initialize()
image = ee.Image("JRC/GSW1_0/GlobalSurfaceWater")

image.getInfo()

surfwater = image.select('occurrence')


# llx = -42
# lly = -9
# urx = -36
# ury = -2
# geometry = [[llx,lly], [llx,ury], [urx,ury], [urx,lly]]
geometry = ee.Geometry.Rectangle([-42, -9, -36, -2])
geometry = geometry['coordinates'][0]

task_config = {
    'description': 'GlobalSurfaceWater',
    'region':geometry}


tsk=ee.batch.Export.image.toDrive(image=surfwater,fileNamePrefix='GlobalSurfaceWater',region=geometry)

tsk.start()

surfwater.getDownloadURL(task_config)

# Export the image, specifying scale and region.
# task = ee.batch.Export.image(surfwater,'GlobalSurfaceWater', task_config);

# task.start()
