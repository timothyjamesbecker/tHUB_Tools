import os
import re
import sys
import cPickle as pickle
import file_tools

ft = file_tools.File_Tools()
code_path = '../LODES/state_codes.csv'
codes = ft.read_csv(code_path,[])
code_header = codes[1]
codes = codes[2:]
state_map = {}
for i in range(0,len(codes)):
    state_map.update({codes[i][1].zfill(2):codes[i][2]})
print(state_map)

#data has all tabulated blocks
base = '../DATA_LEHD/'
files = os.listdir(base)

reg_ex = '^ct_od_aux' #prefix you want
matched = []
for f in files:
    m = re.search(reg_ex, f)
    if m is not None:
        print('Found: '+f)
        matched.append(f)

unique_states = set()
for f in matched:
    table = ft.read_gzip_csv(base+f,[])
    name = table[0]
    header = table[1]
    data = table[2:]
    print(name)
    print(header)
    print(data[0:5])
    for row in data:
        if(int(row[1][2]) > 0):
            unique_states.add(row[1][0:2])
        
unique_states = list(unique_states)
unique_states.sort()
