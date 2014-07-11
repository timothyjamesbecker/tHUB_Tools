import align
import distance
import copy
import numpy as np
import time
from collections import Counter

#given a sequence S of length n produces
#k variantions around S with rate m and size l
def variations(S,k,m,l):
    n = len(S)       #length of S
    u = set(S)       #unique symbols set of S
    T = [S]          #new set of sequences made starting at S
    for i in range(0,k):
        t = copy.deepcopy(S)         #copy out S      
        r = np.random.randint(1,max(n*l,2)) #pick how many tries on the seq using m
        for x in range(0,r):
            if np.random.binomial(1,m)==1:        #mutation rate success ==1
                ty = np.random.randint(0,2)       #type of the mutation
                y = np.random.randint(0,len(t)-1)   #pick a random position
                if ty==0:   #rand I=0 +1
                    z = np.random.choice(list(u)) #select a random symbol from u
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

#resolve directed edges to undirected
#u@v==v@u
def edge_seq(A):
    S = []
    for i in range(0,len(A)):
        s = []
        for j in range(1,len(A[i])):
            s += ['@'.join([str(A[i][j-1]),str(A[i][j])])]
        S += [s]
    return S          

def rev(e):
    x = e.split('@')
    return '@'.join(x[::-1])
            
#find the preditibilty entropy of
#A using the amount of repeated patterns
def entropy(A,method):
    if method=='shannon':
        F,c = {},0
        for i in range(0,len(A)):
            for j in range(0,len(A[i])):
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
        
                   
#run the test code here, this is a dual path tester
T = [0,0,12,2,10,1,0,0,1,1]
L = variations(T,10,0.5,0.5)
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
a = align.Align(w,rp,nn,k)

start = time.time()
for i in range(0,1):
    S = copy.deepcopy(L)
    print("Done\nComputing Alignment")
    a.pair(L,'cstar')
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
print('consensus accuracy is %s percent'%(100*max((1.0-error/len(T)*1.0),0)))
print('time is %s ms'%((stop-start)*1000.0))

