import os
import re
import sys
import file_tools

#using the tabulated FIPS, making unique, sorting etc...
def get_fips(row):
    return ''.join(row[0:1])

def get_fips2(row):
    return ''.join(row[10:14])

# A Census Block FIPS code has 15 digits and is structured as follows:
# AA BBB CCCCCC D EEE
# A = State (2 digit FIPS code)
# B = County (3 digit FIPS code)
# C = Tract (6 digit FIPS code)
# D = Block Group (1 digit FIPS code)
# E = Block (3 digit FIPS code)
def decompose_fips(fips):
    d_fips = '0','0','0','0','0'
    try:
        d_fips = fips[0:2],fips[2:5],fips[5:11],fips[11:12],fips[12:15]
    except: print('FIPS not formated correctly!')
    return d_fips

def process_coltab(path,files,types):
    raw_fips = [] #blank data structure
    #for each file or state...
    for f in files:
        print('processing: '+f)
        text = ft.read_zip_csv(path+f,types) #[0]->dir, [1+]->files
        header = text[1][1] #header here
        #print(header)
        for i in range(2,len(text[1])): #[1][1] is the header
            row = text[1][i]     #get next line
            raw_fips.append(get_fips2(row))
    return raw_fips

def process_assignments(path,files,types):
    raw_fips = []
    for f in files:
        print('processing: '+f)
        text = ft.read_zip_csv(path+f,types) #read all files from .zip
        s = 'AIANNH.txt' #use this one?
        for i in range(1,len(text)):
            m = re.search(s,text[i][0])
            if m is not None:
                print('Found: '+text[i][0])
                header = text[i][1] #header here
                print(header)
                print(str(len(text[i])-2)+' rows of data present...\n')
                for j in range(2,len(text[i])): #data rows here
                    row = text[i][j] #get next line
                    raw_fips.append(get_fips(row))
    return raw_fips

            
ft = file_tools.File_Tools()
#data has all tabulated blocks
base = '../DATA_FIPS/'
out_path = '../'
files = os.listdir(base)
#files.remove('census_states.txt')
print(files)

name = 'fips_blocks.gz'
header = 'FIPS15_Block'
fips = process_assignments(base,files,[])        
len_all = len(fips)
print('Size of all FIPS = ' + str(len_all))
print('Sorting Codes...')
fips.sort()
print('Acending Order Completed')
#check for funky string....
#len([i for i in fips if re.search('T',i) is not None])
bad = len([i for i in fips if re.search('\d{15}',i) is not None])
print("There are " +str(bad)+' codes that don\'t conform')
fips = [[i] for i in fips]
fips = [name]+[[header]]+fips
print('Test Set:')
print(fips[0:10])
ft.write_csv_gzip(out_path+name,fips,[])



    
    
    












