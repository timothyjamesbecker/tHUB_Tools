#lehd_agregate.py v 2.4, 10/20/2013-02/23/2014
#Timothy Becker, UCONN/SOE/CSE/Graduate Research Assistant
#General Purpose LEHD Agregation Script
#takes Agregation char = {S,C,T,G} and lehd file directory
#and applies an optimal agregation in Theata(n) time: n=#rows
#File_Tools.read_gzip_csv and write_csv_gzip outperform numpy loadtxt
#by at least 2-3X and np.sum() outperforms any other method by 2-3X
#
#algo:  [1] split into keys and data where keys are geocode.
#       [2] keys are truncated and then mapped to unique keys
#       [3] ordering is maintained and effiecient numpy sumation
#       [4] performs the final agregation calculation on uint32 s


import numpy as np
import os
import re
import sys
import time
import file_tools

#convient enumeration to extract a type
def lehd_type(name):
    m = re.search('od{1}|wac{1}|rac{1}',name)
    if m is not None: return m.group(0).upper() #file type
    else: return None

#user must know what they have in the input    
def agr(a):
    select ={'G':lambda x: x[0:12],
             'T':lambda x: x[0:11],
             'C':lambda x: x[0:5],
             'S':lambda x: x[0:2]}
    return select[a]

#for type = 'OD' use this to extract single keys
def decomp_keys(K,t,s):
    if t=='OD': return [k.split(s) for k in K]
    else: return K
    
#read a lehd file f and build a np array and key set
#with associated array indexes
def load(f):
    ft = file_tools.File_Tools()
    temp = ft.read_gzip_csv(f,[]) #ft is a 2X speed up over numpy.loadtxt()
    n,name,header,d,t,k = len(temp[2:]),'',[],[],None,None
    #select the type
    select = {'OD': {'d':lambda x: [r[2:-1] for r in x],
                     'k':lambda x: [r[0:2]  for r in x]},
              'WAC':{'d':lambda x: [r[1:-1] for r in x],
                     'k':lambda x: [[r[0]]  for r in x]},
              'RAC':{'d':lambda x: [r[1:-1] for r in x],
                     'k':lambda x: [[r[0]]  for r in x]}}
    if n>0:
        print ('File: '+temp[0])
        name   = temp[0]
        t = lehd_type(name)
    if n>1:
        print 'Header: ',
        print(temp[1])
        header = temp[1]
    if n>2 and t is not None:
        #seperate the data from keys, indecies keep assciation
        d      = select[t]['d'](temp[2:])
        k      = select[t]['k'](temp[2:])
    return name,t,header,np.array(np.array(d,dtype=np.float32),dtype=np.uint32),k

def store(name,header,R):
    ft = file_tools.File_Tools()
    R = [name]+[header]+R
    ft.write_csv_gzip(name,R,[])

#a mapping of unique dynamically truncated keys to data indecies
def key_mapper(keys,t,lev,s):
    K,M,a,x = [],{},agr(lev),0
    if t==None: return M #all depends on the agregation level picked
    if t=='OD': #truncate and concat keys (can become unsorted!!!)
        K = [a(k[0])+s+a(k[1]) for k in keys]
        I = sorted(range(len(K)),key=lambda x: K[x]) #correct unsort
    else: #wac,rac just truncate
        K = [a(k[0]) for k in keys]
        I = range(0,len(keys))
    #now we are sorted and ready to tally up marks
    for i in I: #nonlinear indecies in sorted order now...
        if M.has_key(K[i]): M[K[i]].append(i)
        else: M.update({K[i]:[i]})
    return M
    
#verify each key is mapped to an index
def map_is_correct(M,keys):
    E = [False for i in keys]
    for k in M.keys(): #check all keys
        for i in M[k]: #each index list
            E[i] = True
    return all(E)

#for key in the map, sum each colum
def agregate(M,data):
    i,K = 0,sorted(M.keys())
    D = np.zeros((len(K),data.shape[1]),dtype=np.uint32)
    for k in K: #iterate on keys in sorted order
        D[i] = np.sum(data[M[k],:],axis=0) #fill D in order
        i+=1
    return D,K #return the two halves

#reconstruct a list of list
def recomp(K,D):
    L = []
    for i in range(0,len(K)):
        if type(K[i]) is list and len(K[i])>1: L.append(K[i]+list(D[i]))
        else: L.append([K[i]]+list(D[i]))
    return L

a_lev = sys.argv[1].upper()
path = os.path.abspath(sys.argv[2])
rawf = os.listdir(path)
files = []
for f in rawf: #load only files that conform to '_YYYY.csv.gz'
    m = re.search('_[0-9]{4}.csv.gz$',f)
    if m is not None: files.append(f)
files.sort() #sort names so that they are done in order
if sys.platform[0:4] == 'linux': div = '/'
elif sys.platform == 'darwin': div = '/'
else: div ='\\'
files = [path+div+f for f in files]
print(files[0])
suffix = {'S':'.state.csv.gz',
          'C':'.county.csv.gz',
          'T':'.tract.csv.gz',
          'G':'.group.csv.gz'}
for f in files:
    total_s = time.time()
    #around 2 minutes on my machine to read and load
    start = time.time()
    name,t,header,data,keys = load(f)
    stop = time.time()
    if len(data)>0: #protect against the empty lehd files
        print('FT: Elapsed time was %g seconds' % (stop - start))
        print('NP: To load %i records' % data.shape[0])
        print 'First data line: ',
        print(data[0])
        #this was the bottleneck, much faster now
        start = time.time()
        M = key_mapper(keys,t,a_lev,'@')
        stop = time.time()
        print('KM: Elapsed time was %g seconds' % (stop - start))
        print('KM: Unique Agregate keys: %s' % len(M.keys()))
        print('Verified: %s' % map_is_correct(M,keys))
        s = sorted(M.keys())[0]
        print('Indecies: %s Mapped to Key: %s'%(M[s],s))
        #summation is fast with numpy array of uint32 s
        D,K = agregate(M,data) #K is the unique keys in sorted double row order
        print('Summed rows 0-5:')
        print(D[0:5])
        print('Key rows 0-5:')
        print(K[0:5])
        R = recomp(decomp_keys(K,t,'@'),D)
        print('Reformed Rows: 0-5:')
        print(R[0:5])
        name = name.replace('.csv.gz',suffix[a_lev])
        print('Naming result as: %s'%name)
        print('Writing %s to Disk'%name)
        store(name,header[0:-1],R)
        print('Finished Processing %s'%name)
        print('%s records stored in disk'%len(R[1:]))
        total_e = time.time()
        print('Total system Processing Time was %d seconds\n'%(total_e-total_s))
    else: print('%s File Empty, moving to next file'%name)


