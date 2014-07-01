#tHUB Project UCONN: http://www.thub.uconn.edu
#GTFS SQL Import Tool v 0.7
#Timothy Becker, Graduate Research Assistant

#standard python includes for win7 / python 2.7 / numpy
import sys
import os
from subprocess import call

#helper python functions for win7 / python 2.7 / csv
import gtfs2mssql

drv,srv,db,conn,gtfs_dir = '{SQL Server}','arc-gis','tHUB',None, sys.argv[1]
for arg in sys.argv: print arg #argv[0] will be this file name

#validate the GTFS here using googletransitfeed python code...
transitfeed = 'GTFS_Import\\transitfeed\\feedvalidator.exe'
allowed = ['True','true','T','t',True]
if sys.argv[2] in allowed: call([transitfeed,gtfs_dir])

#use new GTFS2MSQL class code here...
#initialize the GTFS2MSSQL parser
#maybe some extra with protection here?
with gtfs2mssql.GTFS2MSSQL(drv,srv,db,gtfs_dir) as gtfs: gtfs.run()




            



