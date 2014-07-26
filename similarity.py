import itertools as it
import numpy as np
import Levenshtein as lv
import spatial_distance

#does pairwise simulairty with reversal under prenalty
#returning the d,r matricies with the min_sp estimator index and cost
def partition_fwd_rev(ss,rp):
    n,z = len(ss),0
    m = max([len(i) for i in ss])
    d,r = np.zeros((n,n),dtype=float),np.zeros((n,n),dtype='bool')
    pairs = [(j,k) for j,k in it.combinations(range(0,n),2)]
    print('Computing %s Partioning Pairs'%(n*(n-1)/2))
    for j,k in pairs:
        a = ''.join([unichr(i)for i in ss[j]])
        b = ''.join([unichr(i)for i in ss[k]])
        x = lv.distance(a,b)
        y = lv.distance(a,b[::-1])+rp
        if x<y: d[j][k] = x
        else:   d[j][k],r[j][k] = y,True
        d[k][j],r[k][j],z = d[j][k],r[j][k],z+1 #symetric, so save time
        if z%int(1E3)==0: print '.',
    print('')
    c = np.argmin([np.sum(d[:,j]) for j in range(0,n)])
    t = np.min([np.sum(d[:,j]) for j in range(0,n)])
    return {'d':d,'r':r,'min_sp':{'i':t,'cost':c}} 

#converts to UTF16 in python 2.7 and runs a fast greedy median
#string finder algorithm on the results of the full and fwd rev partitions
def all_median(A,p):
    all_u = [''.join([unichr(i) for i in j]) for j in A] #convert to UTF-16 0-2^16 range
    fwd_i,rev_i = split(A,p['r'])                    #split from the r matrix
    fwd_u = [''.join([unichr(i) for i in j]) for j in fwd_i]
    rev_u = [''.join([unichr(i) for i in j]) for j in rev_i]
    all_m = lv.median(all_u) #test it on all directions
    fwd_m = lv.median(fwd_u)
    rev_m = lv.median(rev_u)                        
    print('fwd==rev? %s'%(fwd_m==rev_m))
    all_med = [ord(i) for i in all_m]
    fwd_med = [ord(i) for i in fwd_m]
    rev_med = [ord(i) for i in rev_m]
    return {'all':all_med,'>':fwd_med,'<':rev_med} #> partition is always larger

#use this to flip the reversed partitions
def flip_partition(P):
    return [i[::-1] for i in P]

#simple version without fwd rev partitions
def median(A):
    u = [''.join([unichr(i) for i in j]) for j in A]
    u_m = lv.median(u)
    return [ord(i) for i in u_m]

#applies the partition parameter from table p
#to the list of list sequence set A
def split(A,r):
    fwd_i = list(np.where(r==0)[0])
    rev_i = list(np.where(r==1)[0])
    if len(rev_i)>len(fwd_i): fwd_i,rev_i = rev_i,fwd_i
    fwd,rev = [],[]
    for i in fwd_i: fwd+=[A[i]]
    for i in rev_i: rev+=[A[i]]
    return fwd,rev
                           
#find the preditibilty entropy of
#A using the amount of repeated patterns
def entropy(A,method):
    if method=='shannon':
        F,c = {},0
        for i in range(0,len(A)):
            for j in range(0,len(A[i])):
                if A[i][j]!='-':
                    if type(A[i][j])==str:
                        if F.has_key(A[i][j]):        F[A[i][j]]+=1
                        elif F.has_key(rev(A[i][j])): F[rev(A[i][j])]+=1 
                        else: F[A[i][j]] = 1
                        c+=1.0
                    else:
                        if F.has_key(A[i][j]): F[A[i][j]]+=1
                        else: F[A[i][j]] = 1
                        c+=1.0
        for k in F: F[k] = F[k]/c
        v = np.asarray(F.values())
        e = -1*np.sum(v*np.log2(v))
        return F,e
    else: return {},0.0    

#find the edge preditibilty entropy of
#A using the amount of repeated patterns
def edge_entropy(A,method):
    if method=='shannon':
        F,c = {},0
        for i in range(0,len(A)):
            for j in range(1,len(A[i])):
                pk = '@'.join([str(A[i][j-1]),str(A[i][j])])
                if F.has_key(pk): F[pk]+=1
                else: F[pk]=1
                c+=1.0
        #for k in F: F[k] = F[k]/c
        v = np.asarray(F.values())
        e = -1*np.sum(v*np.log2(v))
        return F,c,e #return the counts instead
    else: return {},0.0 