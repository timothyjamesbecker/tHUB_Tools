import os
import re
import sys
import cPickle as pickle
import file_tools

# A Census Block FIPS code has 15 digits and is structured as follows:
# AA BBB CCCCCC D EEE
# A = State (2 digit FIPS code)
# B = County (3 digit FIPS code)
# C = Tract (6 digit FIPS code)
# D = Block Group (1 digit FIPS code)
# E = Block (3 digit FIPS code)
def substring_decomp(fips):
    #default search is None so all([B,G,T,C,S]==None)->True
    B,G,T,C,S,n = None,None,None,None,None,len(fips)
    b = re.search('\d{15}', fips) #match for block
    g = re.search('\d{12}', fips) #match for group
    t = re.search('\d{11}', fips) #match for tract
    c = re.search('\d{5}' , fips) #match for county
    s = re.search('\d{2}' , fips) #match for state
    #gaurded, matched-base assignment of string ranges
    if s is not None: S = fips[0:2]
    if c is not None: C = fips[2:5]
    if t is not None: T = fips[5:11]
    if g is not None: G = fips[11:12]
    if b is not None: B = fips[12:15]
    if not all([i==None for i in [B,G,T,C,S]]): #not the default search
        if n == 2:  return [S]
        if n == 5:  return [S,S+C]
        if n == 11: return [S,S+C,S+C+T]
        if n == 12: return [S,S+C,S+C+T,S+C+T+G]
        if n == 15: return [S,S+C,S+C+T,S+C+T+G,S+C+T+G+B]
    else:
        print('Format Error on: '+fips)
        return None
    
ft = file_tools.File_Tools()
#data has all tabulated blocks
tools = '../'
base = tools+'DATA_FIPS/'
out_path = tools+'fips_sql_table.csv'

name = 'fips_blocks.gz'
header = ['state', 'county', 'tract', 'block', 'group']
fips = ft.read_gzip_csv(base+name,[])[2:]
fips = [i[0] for i in fips]

table = []
for f in fips:
    table.append(substring_decomp(f))

ft.write_csv(out_path,header,table,[])
    



