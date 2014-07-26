import align
import distance
import copy
import itertools as it
import numpy as np
import scipy as sp
import jellyfish
import editdistance
import Levenshtein
import time
from collections import Counter


#given a sequence S of length n produces
#k variantions around S with rate m and size l
def variations(S,k,m,l,e):
    n = len(S)       #length of S
    u = set(S)       #unique symbols set of S
    T = [S]          #new set of sequences made starting at S
    e = set(range(n+1,n+int(e*(n+1))))
    for i in range(0,k-1):
        t = copy.deepcopy(S)         #copy out S      
        r = np.random.randint(1,max(n*l,2)) #pick how many tries on the seq using m
        for x in range(0,r):
            if np.random.binomial(1,m)==1:        #mutation rate success ==1
                ty = np.random.randint(0,2)       #type of the mutation
                y = np.random.randint(0,len(t)-1)   #pick a random position
                if ty==0:   #rand I=0 +1
                    z = np.random.choice(list(u)+list(e)) #select a random symbol from u
                    t = t[0:y]+[z]+t[y+1:]        #insertion of z into t
                elif ty==1: #rand S=1 +0
                    #v = u-set(S[y])
                    z = np.random.choice(list(u)) #select a random symbol from u-S[y]
                    t = t[0:y-1]+[z]+t[y+1:]      #substitution of pos y
                else:       #rand D=2 -1
                    t = t[0:y]+t[y+1:]            #deletion of pos y
        if np.random.binomial(1,pow(m,0.5))==1: t = t[::-1] #reversals
        T+=[t]
    return T
        
#given an aligned sequence set
#produce the consensus sequence
def consensus(A):
    #n=number of sequences, m=length of each sequence, C consensus
    n,m = len(A),len(A[0])
    A = np.asarray(A)    #easier column ops
    C = list(A[0,:])     #consensus slice init
    for j in range(0,m): #each column
        c = {}
        for i in range(0,n): #each row
            if c.has_key(A[i,j]): c[A[i,j]]+=1
            else: c[A[i,j]] = 1
        k = c.keys()[np.argmax(c.values())]
        if k!='-': C[j] = int(k)
        else:      C[j] = k

    i = len(C)-1            #trim and right hand
    while C[i]=='-' and i>0: i -= 1 #insertion chars
    return C[0:i+1]

#given the sequences, find all possible starts
#and stops, allong with all edge depths
#this will be a profile weight map PWM
#use thresholding or 1D edge detection
def paths(A,method):
    U = sorted(list(set([i for j in A for i in j])))
    i_u = {i:U[i] for i in range(0,len(U))} #unique node enumeration
    u_i = {U[i]:i for i in range(0,len(U))} #and reversal
    PWM,e = {'start':{},'stop':{}},0 #edge enumeration variable=e
    for i in range(0,len(A)): #each sequence
        if PWM['start'].has_key(u_i[A[i][0]]): PWM['start'][u_i[A[i][0]]]+=1 #keep track
        else:                                  PWM['start'][u_i[A[i][0]]] =1 #of terminal
        if PWM['stop'].has_key(u_i[A[i][-1]]): PWM['stop'][u_i[A[i][-1]]]+=1 #nodes plus
        else:                                  PWM['stop'][u_i[A[i][-1]]] =1 #the edges
        for j in range(1,len(A[i])): #each edge in the sequence
            PK = sorted([u_i[A[i][j-1]],u_i[A[i][j]]]) #stored in sorted order
            s = '@'.join([str(t) for t in PK])
            if PWM.has_key(s): PWM[s]+=1
            else:              PWM[s]=1
        
    C,c,pk = [],max(PWM['start']),PWM.keys()
    pk.remove('start')
    pk.remove('stop')
    n = len(U)
    G = np.zeros((n,n),dtype='float')
    L = [{} for i in i_u.keys()]
    for s in pk:
        t = s.split('@')
        p,k = [int(i) for i in t]
        L[p][k],L[k][p] = PWM[s],PWM[s]
        G[p,k] = G[k,p] = PWM[s]
        
    for i in range(0,n):
        G[i] = 1.0-(G[i]/sum(G[i]))
        x = list(np.where(G[i]==1)[0])
        if len(x)>0: G[i,x] = 0.0
    
    #clear out the 1.0 to zero some how...
    #S = sp.sparse.csr_matrix(G)
    #D = sp.sparse.csgraph.dijkstra(S,return_predecessors=True)
    
    #for each start to stop pair...
    #find a non repeating maximal weight path
    
    #while c != max(PWM['stop']):
        
    #       C+=[max()]
    return PWM,L,G#,S,D       

# given an adjacency list L
# and start and stop node q0, qf
# find a maximal non-repeating 
# path from q0 to qf
#def maximal_path(q0,qf,L):
    
def test_edit_dist(x):
    s1 = '12012014321231200112211'
    s2 = '1300201231200112211'
    seq1 = [1,2,0,1,2,0,1,4,3,2,1,2,3,1,2,0,0,1,1,2,2,1,1]
    seq2 = [1,3,0,0,2,0,1,2,3,1,2,0,0,1,1,2,2,1,1]
    pos = np.asarray([[0,0],[0,1],   #0 and 1 are nn
                      [2,0],[2,1],   #2 and 3 are nn
                      [4,0],[4,1],   #4 and 5 are nn
                      [6,0],[6,1],   #6 and 7 are nn
                      [8,0],[8,1],   #8 and 9 are nn
                      [9,0],[9,1],   #10 and 11 are nn
                      [10,0],[10,1]],#12 and 13 are nn
                      dtype=float)
                      
    #modify this to ensure it is a non-connected k-nn
    nn = distance.ann(pos,1)[1][:,1:]
    k = 0
    rp = 1
    w = {'M':lambda x:0,'I':lambda x:1,'D':lambda x:1,
         'S':lambda x:2, 'P':lambda x:0.5 }
    a = align.Align(w,rp,nn,k)
    
    u,v = 0,0
    t0 = time.time()
    for i in range(0,int(x)):
        u = jellyfish.levenshtein_distance(s1,s2)
    t1 = time.time()
    t2 = time.time()
    for i in range(0,int(x)):
        v = Levenshtein.editops(s1,s2)
    v = Levenshtein.distance(s1,s2)
    t3 = time.time()
    t4 = time.time()
    for i in range(0,int(x)):
        #v = a.edit_dist(seq1,seq2)
        #w = a.edit_graph(seq1,seq2)
        #w = a.levenshtein(seq1,seq2)
        w = 1
    w = a.edit_dist(seq1,seq2)
    t5 = time.time()
    #w = a.edit_dist(seq1,seq2)
    print('editdist  dist = %s'%v)
    print('seq edit  dist = %s'%w)
    print('editdist  runtime is %s seconds'%(t3-t2))
    print('seq edit  dist = %s'%(t5-t4))
    
    #editdistance.eval([1,2],[2,1])

def test_pair():
    T = [3,1,3,1,3,3,5,7,5,1,5,7,9,1,0,0,0,0,2,2,2,4,6,7,9,9,11,11]
    L = variations(T,2000,0.75,0.85,0.5)
    
    t0 = time.time()
    p = partion_fwd_rev(L,1)
    t1 = time.time()
    
    pos = np.asarray([[0,0],[0,1],   #0 and 1 are nn
                      [2,0],[2,1],   #2 and 3 are nn
                      [4,0],[4,1],   #4 and 5 are nn
                      [6,0],[6,1],   #6 and 7 are nn
                      [8,0],[8,1],   #8 and 9 are nn
                      [9,0],[9,1],   #10 and 11 are nn
                      [10,0],[10,1]],#12 and 13 are nn
                      dtype=float)
                      
    #modify this to ensure it is a non-connected k-nn
    nn = distance.ann(pos,1)[1][:,1:]
    k = 0
    rp = 1
    w = {'M':lambda x:0,'I':lambda x:1,'D':lambda x:1,
         'S':lambda x:2, 'P':lambda x:0.5 }
    a = align.Align(w,rp,nn,k)
    t2 = time.time()
    #a.min_sp(L)
    t3 = time.time()

    print('editdist based search %s seconds'%(t1-t0))
    print('seqedit  based search %s seconds'%(t3-t2))

    return L,a,p    

def all_median(A):
    all_u = [''.join([unichr(i) for i in j]) for j in A]       #convert to UTF-16 0-2^16 range
    p = partion_fwd_rev(all_u,1)                               #pairwise edit dist partioning
    fwd_u,rev_u = split(all_u,p[1])                            #split from the r matrix
    all_m = Levenshtein.median(fwd_u+[i[::-1] for i in rev_u]) #test it on all directions
    fwd_m = Levenshtein.median(fwd_u)                          #do approximate greedy
    rev_m = Levenshtein.median(rev_u)                          #median
    all_med = [ord(i) for i in all_m]
    fwd_med = [ord(i) for i in fwd_m]
    rev_med = [ord(i) for i in rev_m]
    return all_med,fwd_med,rev_med

def split(L,r):
    s = [0,0]
    fwd_i = list(np.where(r[0]==0)[0])
    rev_i = list(np.where(r[0]==1)[0])
    if len(rev_i)>len(fwd_i): fwd_i,rev_i = rev_i,fwd_i
    fwd,rev = [],[]
    for i in fwd_i: fwd+=[L[i]]
    for i in rev_i: rev+=[L[i]]
    return fwd,rev
    
        
        

#build kmer subsequences with '@' delimiter
#a single edge would then be u@v
def kmer(A,k):
    S = []
    for i in range(0,len(A)):
        s = []
        for j in range(k-1,len(A[i])):
            s += ['@'.join([str(A[i][l]) for l in range(j-k,j)])]
        S += [s]
    return S

def rev(e):
    x = e.split('@')
    return '@'.join(x[::-1])

def equal_2d(x,y):
    if x.shape != y.shape: return [list(i) for i in x]
    L = []
    for i in range(0,x.shape[0]):
        for j in range(0,x.shape[1]):
            if x[i][j]!=y[i][j]: L+=[[i,j]]
    return L
            
            
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


def partion_fwd_rev(ss,rp):
    n,z = len(ss),0
    m = max([len(i) for i in ss])
    d,r = np.zeros((n,n),dtype=float),np.zeros((n,n),dtype='bool')
    pairs = [(j,k) for j,k in it.combinations(range(0,n),2)]
    print('Computing %s Partioning Pairs'%(n*(n-1)/2))
    for j,k in pairs:
        x = Levenshtein.distance(ss[j],ss[k])
        #x = editdistance.eval(ss[j],ss[k])
        y = Levenshtein.distance(ss[j],ss[k][::-1])+rp
        #y = editdistance.eval(ss[j],ss[k][::-1])+rp
        if x<y: d[j][k] = x
        else:   d[j][k],r[j][k] = y,True
        d[k][j],r[k][j],z = d[j][k],r[j][k],z+1 #symetric, so save time
        if z%int(1E3)==0: print '.',
    print('')
    c = np.argmin([np.sum(d[:,j]) for j in range(0,n)])
    t = np.min([np.sum(d[:,j]) for j in range(0,n)])
    return d,r,c,t       

#--------------------------------------------------------------------------

accuracy,runtime = [],[]       
for d in range(0,1):                   
    #run the test code here, this is a dual path tester
    T = [0,4,2,6,12,8]
    L = variations(T,20,0.25,0.5,0.1)
    #spatial pos for ids 0,1,2,3,4,5,6,7,8,9,10,11,12,13 to do nn on
    pos = np.asarray([[0,0],[0,1],   #0 and 1 are nn
                      [2,0],[2,1],   #2 and 3 are nn
                      [4,0],[4,1],   #4 and 5 are nn
                      [6,0],[6,1],   #6 and 7 are nn
                      [8,0],[8,1],   #8 and 9 are nn
                      [9,0],[9,1],   #10 and 11 are nn
                      [10,0],[10,1]],#12 and 13 are nn
                      dtype=float)
    x = len(L)
    y = max([len(i) for i in L])
    s = max([max([len(str(L[i][j])) for j in range(0,len(L[i]))]) for i in range(0,x)])
    print('\nStarting Alignment:') 
    for r in L:
        for i in r:
            l = len(str(i))
            print str(i).ljust(s+1),
        print('')
        
    #set up params
    w = {'M':lambda x:0,'I':lambda x:1,'D':lambda x:1,
         'S':lambda x:1, 'P':lambda x:0.5 }
    rp = 1
    k = 1
    nn = distance.ann(pos,k)[1][:,1:]
    print("vertex nn:")
    print(nn.T[0])
    a = align.Align(w,rp,nn,0)
    
    start = time.time()
    for i in range(0,1):
        S = copy.deepcopy(L)
        print("Done\nComputing Alignment")
        a.pair(L,'rand')
    stop = time.time()
    
    print('total cost:%s'%(a.cost))
    center = ''.join([str(i).ljust(s+1) for i in S[a.c]])
    print('center used: '+center)
    for r in a.s:
        for i in r:
            l = len(str(i))
            print str(i).ljust(s+1),
        print('')
    
    print('initial string:\t%s'%''.join([str(i).ljust(s+1) for i in T]))
    C = list(consensus(a.s))
    w = {'M':lambda x:0,'I':lambda x:1,'D':lambda x:1,
         'S':lambda x:1, 'P':lambda x:0.5 }
    a2 = align.Align(w,rp,nn,k)
    e1,e2 = a.edit_dist(T,C),a2.edit_dist(T,C[::-1])
    if e1<e2:
        error = e1
        print('consensus string:\t%s'%''.join([str(i).ljust(s+1) for i in C]))
    else:
        error = e2
        print('consensus string:\t%s'%''.join([str(i).ljust(s+1) for i in C[::-1]]))
    accuracy += [100*max((1.0-error/len(T)*1.0),0)]
    runtime  += [(stop-start)*1000.0]
    print('consensus accuracy is %s percent'%(100*max((1.0-error/len(T)*1.0),0)))
    print('time is %s ms'%((stop-start)*1000.0))

    print('average accuracy is %s'%(np.mean(accuracy)))
    print('average time is %s seconds'%(np.mean(runtime)/1000.0))