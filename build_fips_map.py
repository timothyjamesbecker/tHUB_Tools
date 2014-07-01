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
def decompose_fips(fips,t=int):
    m = re.search('\d{15}', fips)
    d_fips = '0','0','0','0','0'
    if m is not None:
        d_fips = fips[0:2],fips[2:5],fips[5:11],fips[11:12],fips[12:15]
        #d_fips = [t(i) for i in d_fips] #type conversion if needed
    else: print('Error with: '+fips)
    return d_fips

def merge(m1,m2):
    m,E = {},None #destination map
    for k in set(m1.keys()+m2.keys()):
        try:
            m.setdefault(k,[]).append(m1[k])        
        except KeyError: pass
        try:
            m.setdefault(k,[]).append(m2[k])          
        except KeyError:pass

    for k_i in m:
        if type(m[k_i]) is list:
            v = m.pop(k_i)                  #pop the value list for key k
            n = {}                          #non-duplicate map
            try:
                if type(v[0]) is list: v = v[0]
                for e in v:                     #for every item
                    for k_j in e.keys():        #for each key
                        n.update({k_j:e[k_j]})  #dig out the items
                m.update({k_i:n})               #put back the items
            except Exception:
                E = v
                m.update({k_i:v})
    return m,E

#number of leaves or terminal nodes of the form 'x':'x'
def size(M):
    if type(M) is not dict: return 0
    if all([M[i]==i for i in M]): return len(M.keys())
    else:
        n = 0
        for k in M:
            n += size(M[k])
        return n


#print out terminal nodes
def printmap(M,L):
    if type(M) is not dict: return 
    if M.keys()==M.values(): L.extend(M.keys())
    else:
        for k in M: printmap(M[k],L)
        return L

def prefix(fips,pre):
    return [fips[j] for j in [i for i in range(0,len(fips)) if fips[i][0:len(pre)]==pre]]

# A Census Block FIPS code has 15 digits and is structured as follows:
# AA BBB CCCCCC D EEE
# A = State (2 digit FIPS code)
# B = County (3 digit FIPS code)
# C = Tract (6 digit FIPS code)
# D = Block Group (1 digit FIPS code)
# E = Block (3 digit FIPS code)
def decomp(fips,ty=str):
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
        if n == 2:  return [ty(S)]
        if n == 5:  return [ty(S),ty(C)]
        if n == 11: return [ty(S),ty(C),ty(T)]
        if n == 12: return [ty(S),ty(C),ty(T),ty(G)]
        if n == 15: return [ty(S),ty(C),ty(T),ty(G),ty(B)]
    else:
        print('Format Error on: '+fips)
        return None

# returns the value(s) associated with
# the key K in map M (after a decomp of K)
def query(K,M,ty=str):
    m = M
    k = decomp(K,ty)
    try:
        for i in range(0,len(k)):
            if type(m) is dict: m = m[k[i]]
    except KeyError:
        print('Key Error with: '+str(K))
        m = None
    return m

def query_all(L,M,ty=str):
    Q = []
    for i in range(0,len(L)):
        q = query(L[i],M,ty)
        if q is not None: Q.append(q)
        else: print('Error Processing Index: '+str(i))
    return Q

def build_fips(fips):
    fips.sort() #enforce sorted order for algorithm correctness
    i,n,e = 1,len(fips),None #terminal, size, error collection
    debug = [] #list for all errors encountered and recorded
    states,counties,tracts,groups,blocks = {},{},{},{},{} #stubs
    #big letters are for the prior step, small for the post step
    S,C,T,G,B = decomp(fips[0]) #prime the sieve
    B = None         #force the block to be different
    
    fips.extend([fips[-1]]) #add one extra at the end
    
    for f in fips: #for each block code in the list of unique
        #get post step to compare to prior step
        s,c,t,g,b = decomp(f)

        if s!=S or c!=C or t!=T or g!=G or b!=B:
            if B is not None: blocks.update({B:B})
            
        if s!=S or c!=C or t!=T or g!=G:                        
            groups,e = merge(groups,{G:blocks})    
            if e is not None: debug.append([i,f,e])
            blocks = {}                     
            
        if s!=S or c!=C or t!=T:
            tracts,e = merge(tracts,{T:groups})
            if e is not None: debug.append([i,f,e])
            groups = {}
            
        if s!=S or c!=C:
            counties,e = merge(counties,{C:tracts})
            if e is not None: debug.append([i,f,e])
            tracts = {}
            
        if s!=S:
            states,e = merge(states,{S:counties})
            if e is not None: debug.append([i,f,e])
            counties = {}
            
        if i >= n: #clean up last entries here
            blocks.update({b:b})
            groups,e = merge(groups,{g:blocks})    
            if e is not None: debug.append([i,f,e])
            tracts,e = merge(tracts,{t:groups})
            if e is not None: debug.append([i,f,e])
            counties,e = merge(counties,{c:tracts})
            if e is not None: debug.append([i,f,e])
            states,e = merge(states,{s:counties})
            if e is not None: debug.append([i,f,e])
            
        #update the prior step for next round
        S,C,T,G,B = decomp(f)
        i += 1
    return states,debug

def build_map(fips):
    M = {}
    for f in fips:
        F = decomp(f)
        K = getnode(M,F)
        n = len(K)
        if n==0:   M[F[0]]={F[1]:{F[2]:{F[3]:{F[4]:F[4]}}}}
        elif n==1: M[K[0]][F[1]]={F[2]:{F[3]:{F[4]:F[4]}}}
        elif n==2: M[K[0]][K[1]][F[2]]={F[3]:{F[4]:F[4]}}
        elif n==3: M[K[0]][K[1]][K[2]][F[3]]={F[4]:F[4]}
        elif n==4: M[K[0]][K[1]][K[2]][K[3]][F[4]]=F[4]
        else: print("Block %s%s%s%s%s not Unique!"%(f[0],f[1],f[2],f[3],f[4]))
    return M
                   
def getnode(M,F):
    if F==[]: return []
    elif M.has_key(F[0]): return [F[0]]+getnode(M[F[0]],F[1:])
    else: return getnode(M,[])

ft = file_tools.File_Tools()
#data has all tabulated blocks
tools = '../'
base = tools+'DATA_FIPS/'
out_path = tools

name = 'fips_blocks.gz'
fips = ft.read_gzip_csv(base+name,[])[2:]
fips = [i[0] for i in fips]

#for i in range(0,10): print(fips[i])
#fips[0] = '11111111111111a' #test for incorrect fips code
#fips = prefix_filter(fips,'01001') #get only state 09 = CT
#fips_map,debug = build_fips(f)

#print('finished building map')
#query_all(f,fips_map)
#print('finished verifying all keys')

#pickling code
#pkl = 'fips.pkl'
#pkl_out = open(tools+pkl, 'wb')
#pickle.dump(fips_map, pkl_out, pickle.HIGHEST_PROTOCOL)
#pkl_out.close()



    
    
    












