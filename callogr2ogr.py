import subprocess
import modules.getPaths


postgis_user
postgis_pass

subprocess.call(['ogr2ogr','-f','"PostgreSQL"',"-f","GML",polOut + "/" + out_gml])
