#fips.py, 01/28/2014-02/28/2014
#Timothy Becker, UCONN/SOE/CSE/Graduate Research Assistant
#General Purpose FIPS class is a local core-memory based
#Data set and Class design for FIPS processing
#among the many utility functions are the most useful: 
#sup can get the super path of any sub code and likewise
#sub can get the sub tree rooted at the super code
#uses a 5D hash-map data structure with O(1) retrieval times
#provides fast python based access with a DB of FIPS codes

import os
import re
import sys
import time
import cPickle as pickle
import file_tools

# A Census Block FIPS code has 15 digits:
    # AA BBB CCCCCC D EEE
    # A = State (2 digit FIPS code)
    # B = County (3 digit FIPS code)
    # C = Tract (6 digit FIPS code)
    # D = Block Group (1 digit FIPS code)
    # E = Block (3 digit FIPS code)
class FIPS:
    def __init__(self,pkl='fips_int.pkl',flat='fips_blocks.gz'):
        #find the serialized map of US
        self.map = {}
        try:
            start = time.time()
            print('Loading Serialized FIPS Map: '+pkl)
            pkl_file = open(pkl,'rb')
            self.map = pickle.load(pkl_file)
            pkl_file.close()
            stop = time.time()
            print('%s Unique Blocks Accessible'%self.get_size(self.map))
            print('Processing Time: %d seconds'%(stop-start))
        except IOError: #didn't find a preprossed data set, so make one
            print('Error Reading Serialization: '+pkl)
            print('Attempting Rebuild using '+flat)
            ft = file_tools.File_Tools()
            print('Processing '+flat)
            try:
                F = ft.read_gzip_csv(flat,[])[2:]
                F = [i[0] for i in F]
                print('%s block codes processed'%len(F))
                print('Building Map')
                self.map = self.build_map(F)
                print('Finished with %s Unique Blocks'%self.get_size(self.map))
                print('Writing Serialized Object to Disk')
                pkl_out = open(pkl, 'wb')
                pickle.dump(self.map, pkl_out, pickle.HIGHEST_PROTOCOL)
                pkl_out.close()
                print('Done')
            except IOError: print('Error reading '+flat)
            
        #set instance variables
        self.size = self.get_size(self.map)
        self.type = self.get_type()
        
    #def __enter__(self): return self
    #def __exit__(self):
        
    # Checks using regular expressions for a digit-only 2-15 length string
    # decomposes into a list, based on A,B,C,D,E regions of the string
    # can apply type casting to store keys as int for example
    def decomp(self,F,ty=str):
        #default search is None so all([B,G,T,C,S]==None)->True
        B,G,T,C,S,n = None,None,None,None,None,len(F)
        b = re.search('\d{15}', F) #match for block
        g = re.search('\d{12}', F) #match for group
        t = re.search('\d{11}', F) #match for tract
        c = re.search('\d{5}' , F) #match for county
        s = re.search('\d{2}' , F) #match for state
        #gaurded, matched-base assignment of string ranges
        if s is not None: S = F[0:2]
        if c is not None: C = F[2:5]
        if t is not None: T = F[5:11]
        if g is not None: G = F[11:12]
        if b is not None: B = F[12:15]
        if not all([i==None for i in [B,G,T,C,S]]): #not the default search
            if n==2:  return [ty(S)]
            if n==5:  return [ty(S),ty(C)]
            if n==11: return [ty(S),ty(C),ty(T)]
            if n==12: return [ty(S),ty(C),ty(T),ty(G)]
            if n==15: return [ty(S),ty(C),ty(T),ty(G),ty(B)]
        else:
            print('Format Error on: '+F)
        return None

    #put decomposed FIPS code list back together
    #if using int for keys, will repad to form correct FIPS str
    def recomp(self,F):
        if self.type is str: return ''.join(F)
        elif self.type is int:
            Z,S = [2,3,6,1,3],[]
            for i in range(0,len(F)):
                S.append(str(F[i]).zfill(Z[i]))
            return ''.join(S)
    
    #build a unique 5D multimap (tree-like structure) from a list
    #of 15 digit FIPS block codes (any order and duplicates allowed)
    def build_map(self,F):
        M = {}
        for i in F:
            f = self.decomp(i,int)
            k = self.find_node(M,f)
            n = len(k)
            #insertion operations for how many mapped keys match
            if   n==0: M[f[0]]={f[1]:{f[2]:{f[3]:{f[4]:f[4]}}}}
            elif n==1: M[f[0]][f[1]]={f[2]:{f[3]:{f[4]:f[4]}}}
            elif n==2: M[k[0]][k[1]][f[2]]={f[3]:{f[4]:f[4]}}
            elif n==3: M[k[0]][k[1]][k[2]][f[3]]={f[4]:f[4]}
            elif n==4: M[k[0]][k[1]][k[2]][k[3]][f[4]]=f[4]
            else: print("Block %s not Unique!"%f)
        return M

    # returns an inorder list of all
    # the sections of the F that map into M
    # this is equalavent to finding the node where
    # the insertion operation should be applied
    def find_node(self,M,F):
        if F==[]: return []
        elif M.has_key(F[0]): return [F[0]]+self.find_node(M[F[0]],F[1:])
        else: return self.find_node(M,[])

    
    #returns the key type of the fips map
    def get_type(self):
        if self.map.keys() != []:
            t = type(self.map.keys()[0])
        else:
            t = None
        return t
       
    #checks size of the full map
    def get_size(self,M):
        if type(M) is not dict: return 0
        if M.keys()==M.values(): return len(M.keys())
        else:
            n = 0
            for k in M:
                n += self.get_size(M[k])
            return n
        
    # returns the value(s) associated with
    # the key K in map M (after a decomp of K)
    def query(self,K,ty=str):
        m = self.map
        k = self.decomp(K,ty)
        try:
            for i in range(0,len(k)):
                if type(m) is dict: m = m[k[i]]
        except KeyError:
            print('Key Error with: '+str(K))
            m = None
        return m

    # use the query on all elements of map list
    def query_all(self,L,ty=str):
        Q = []
        for i in range(0,len(L)):
            q = self.query(L[i],ty)
            if q is not None: Q.append(q)
            else: print('Error Processing Index: '+str(i))
        return Q

    #like a children function, give all smaller contained
    #codes, example: ST -> C1, C2, ...
    #we assume str only here to resolve issues like 51...
    def sub(self,code,subtree=False):
        k = self.decomp(code)
        if subtree: return self.query(code,self.type)
        else: return self.query(code,self.type).keys()

    #give back the superpath if given a sub code
    #we assume str only here for correctness
    def sup(self,code,superpath=False):
        k = self.decomp(code)
        if superpath:
            L = []
            for i in range(0,len(k)):
                L.append(''.join(k[0:i]+[k[i]]))
            return L
        elif len(k)>1: return k[-2]
        else: return []
            

    
