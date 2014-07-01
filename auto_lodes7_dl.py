#tHUB Project UCONN: http://www.thub.uconn.edu
#LODES 7.0 (US Census 2010 15-digit FIPS geoids)
#http Automated Download Tool v 0.2
#Timothy Becker, Graduate Research Assistant

#run by:
#python .../auto_lodes7.py [lodes_path] [year] [2-letter state list]

#standard python includes for win7 / python 2.7 / numpy /scipy
import errno
import re
import sys
import os
import csv
import hashlib
import gzip
from subprocess import call 

#retrieve the md5sum file for each state and parse to obtain
#a list of file names for auto wget retrival and gz decoding

wget = "C:\\Program Files (x86)\\GnuWin32\\bin\\wget.exe"  #path to wget
ungz = "C:\\Program Files\\7-Zip\\7z.exe"                  #path to 7zip
local_path = sys.argv[1]                                   #local LODES path
url_path   = "http://lehd.ces.census.gov/onthemap/LODES7/" #URL root path
year       = str(sys.argv[2])
states     = sys.argv[3:]    #the 2-letter state abreviations
print os.listdir(local_path) #use to display files at the path

def get_lodes_info(st, local_path, url_path, years):
    #build the path to the next states md5sum file
    st_md5sum_txts = []
    st_md5sum_url = url_path + st + "/lodes_" + st + ".md5sum"
    st_dir = local_path + "\\" + st
    try:
        os.mkdir(st)                           #make the local directory
        call([wget,"-P"+st_dir,st_md5sum_url]) #retrieve the state md5sum file
        st_md5sum_file = os.path.abspath(st_dir)+"\\"+"lodes_"+st+".md5sum"
        print(st_md5sum_file)
        st_md5sum_txts  = read(st_md5sum_file)  #read as list of strings
    except OSError as exc:                      #handle error if already there
        if exc.errno == errno.EEXIST and os.path.isdir(local_path): pass

    names, md5s = [],[]
    for i in st_md5sum_txts:
        if(re.search(year,i[2])!=None):
            names.append(i[2])
            md5s.append(i[0])
    md5s  = [st_md5sum_txts[i] for i in range(0,len(st_md5sum_txts),3)]
    return names,md5s

def split_od_rac_wac(names):
    od,rac,wac = [],[],[]
    for n in names:
        if "_od_" in  n: od.append(n)
        if "_rac_" in n: rac.append(n)
        if "_wac_" in n: wac.append(n)
        
    return od,rac,wac
        

#takes in the filename x.yyy storing as list of strings
def read(filename):
        text = []
        with open(filename, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=' ')
            for row in reader: text.append(row)
        return text

def validate_md5(control_md5, test_file):
    test_md5 = ''
    with open(test_file) as test:
        data = test.read()
        test_md5 = haslib.md5(data).hexdigest()
    if control_md5 == test_md5: return True
    else: return False

#get the md5sum file and parse for each state
#to aquire the exact file names to then DL each
for st in states:
    #get the states filenames
    lodes_names,lodes_md5s = get_lodes_info(st, local_path, url_path, year)
    od,rac,wac = split_od_rac_wac(lodes_names)
    st_dir = local_path + "\\" + st

    for n in od:
        print("processing " + n)
        n_url = url_path + st + "/od/" + n + ".gz" #the csv file URL
        call([wget, "-P"+st_dir, n_url])   #retrieve the csv file
        print(os.listdir(st_dir))
        
    for n in rac:
        print("processing " + n)
        n_url = url_path + st + "/rac/" + n + ".gz" #the csv file URL
        call([wget, "-P"+st_dir, n_url])    #retrieve the csv file
        
    for n in wac:
        print("processing " + n)
        n_url = url_path + st + "/wac/" + n + ".gz" #the csv file URL
        call([wget, "-P"+st_dir, n_url])    #retrieve the csv file

    dl_files = os.listdir(st_dir)






