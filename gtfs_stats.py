import sys
import os
from subprocess import call

def parse(gtfs_name,gtfs_values):
    table = []
    table.append(gtfs_values[0])
    gtfs_values = gtfs_values[1:]
    for i in gtfs_values: table.append(i)
    return table

#takes in the GTFS filename x.txt storing as string
def read(filename):
    text = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, dialect=csv.excel)
        for row in reader: text.append(row)
    return text

#testing code here...

#read a folder location with GTFS files (maybe add .zip functionality...)
fnames = ['agency.txt','calendar.txt','calendar_dates.txt','routes.txt',
          'route_types.txt','trips.txt','stops.txt','stop_times.txt',
          'frequencies.txt','transfers.txt','tranfer_types.txt',
          'shapes.txt','feed_info.txt']
for arg in sys.argv: print arg #argv[0] will be this file name
#dirname = sys.argv[1]
dirname = 'C:\\Users\\tbecker\\Documents\\tHUB\\GTFS_Data\\HARTFORD_googleha_transit_May_21_2013\\'
dfiles = os.listdir(dirname) #just get one for now...
#validate the GTFS here using googletransitfeed python code...
transitfeed = 'GTFS_Import\\transitfeed\\feedvalidator.exe'
if bool(sys.argv[2]) == True: call([transitfeed,dirname])
for dfile in dfiles:
    if dfile in fnames:
        #each gtfs file that matches the processable list in fnames
        print ('\nNow processing ' + dfile)
        
        
        
