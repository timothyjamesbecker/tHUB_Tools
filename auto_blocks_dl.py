#tHUB Project UCONN: http://www.thub.uconn.edu
#Block Relation Table By State (US Census 2010 15-digit FIPS geoids)
#http Automated Download Tool v 0.1
#Timothy Becker, Graduate Research Assistant

#run by:
#python .../auto_blocks.py [save_path]

#standard python includes for win7 / python 2.7 / numpy /scipy
import errno
import re
import sys
import os
import csv
import hashlib
import gzip
from subprocess import call 

wget = "C:\\Program Files\\GnuWin32\\bin\\wget.exe"  #path to wget
ungz = "C:\\Program Files\\7-Zip\\7z.exe"                  #path to 7zip
#local_path = sys.argv[1]                                  #local save path
local_path = 'C:\\Users\\tbecker\\Documents\\tHUB\\DATA_FIPS\\'
url_path   = "http://census.gov/" #URL root path
print os.listdir(local_path) #use to display files at the path

#process state names
def read(filename):
        text = []
        with open(filename, 'rb') as csvfile:
            reader = csv.reader(csvfile,delimiter=',')
            for row in reader: text.append(row)
        return text
    
states_text = read(local_path+'blockassignemtstates.txt')
states = {}
for i in states_text:
    states.update({i[1]:i[0]})
    
#dowload from http://www.census.gov/geo/maps-data/data/baf.html
for st in states:
    #get the states filenames
    print("processing " + st)
    print("-P "+local_path+' '+url_path+states[st])
    call([wget, "-P"+local_path, url_path+states[st]])



