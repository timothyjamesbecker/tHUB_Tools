#lehd_import.py v 2.2 02/11/2014-02/18/2014
#Timothy Becker, UCONN/SOE/CSE/Graduate Research Assistant
#Automated Command-line script for importing large compressed
#multi-year/state LEHD data sets
#Uses the LEHD2MSQL adapter class to autogenerate tables,constraint
#based primary keys and offers a perge method which can delete
#autogenerated table and constraints to maintain primary keys

import sys
import os
import lehd2mssql

drv,srv,db,lehd_dir = '{SQl Server}','arc-gis','tHUB',sys.argv[1]
perge = False
allowed = ['True','true','T','t',True]
if sys.argv[2] in allowed: perge = True
with lehd2mssql.LEHD2MSSQL(drv,srv,db,lehd_dir) as lehd:
    lehd.process_batch(perge)
