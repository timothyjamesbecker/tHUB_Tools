#cstar_align for lists seq v 0.2, 04/16/2014-04/28/2014
#Timothy Becker, UCONN/SOE/CSE

import copy
import numpy as np
import distance
import itertools as it
import time
import sys

# compute the edit graph between two strings using
# the Wagner-Fisher Algorithm and the edit values:
#M,P = Match|Partial, I = Insertion, D = Delete, S = Substitution
def edit_graph(s1,s2,nn):
   u,v = len(s1),len(s2)
   #if u>v: u,v,s1,s2 = v,u,s2,s1
   d = [[0 for col in range(v+1)] for row in range(u+1)]
   b = [['I' for col in range(v+1)] for row in range(u+1)]
   for i in range(0,u+1): d[i][0] = i
   for j in range(0,v+1): d[0][j] = j
   for j in range(1,v+1):
      for i in range(1,u+1):
         k = nn_rank(s1[i-1],s2[j-1],nn) #get nn rank
         if s1[i-1] == s2[j-1]:
            d[i][j],b[i][j] = d[i-1][j-1]+w('M',k), 'M'
         elif k>0: #partial match is a nn match
            d[i][j],b[i][j] = d[i-1][j-1]+w('P',k), 'P' 
         elif d[i-1][j] <= d[i][j-1] and d[i-1][j] <= d[i-1][j-1]:
            d[i][j],b[i][j] = d[i-1][j]+  w('D',k), 'D'
         elif d[i][j-1] <= d[i-1][j-1]:  
            d[i][j],b[i][j] = d[i][j-1]+  w('I',k), 'I'
         else:
            d[i][j],b[i][j] = d[i-1][j-1]+w('S',k), 'S'
   return b, d[u][v]

# Wagner-Fisher Edit Distance Algorithm
# from two strings s1,s2 computes the
# min # of moves to make s1 into s2
def edit_dist(s1,s2,nn):
   u,v = len(s1),len(s2) #weights for edits
   #if u>v: u,v,s1,s2 = v,u,s2,s1
   d = [[0 for col in range(v+1)] for row in range(u+1)]
   for i in range(0,u+1): d[i][0] = i
   for j in range(0,v+1): d[0][j] = j
   for j in range(1,v+1):
      for i in range(1,u+1):
         k = nn_rank(s1[i-1],s2[j-1],nn)
         if s1[i-1] == s2[j-1]: d[i][j] = d[i-1][j-1]
         elif k>0: d[i][j] = d[i-1][j-1]+w('P',k)
         else: d[i][j] = min(d[i-1][j]+  w('D',k),
                             d[i][j-1]+  w('I',k),
                             d[i-1][j-1]+w('S',k))
   return d[u][v]

# align s1 to s2
def edit(s1,s2,nn): #assumes that s2 is larger if there is difference
    m,n,t = len(s1),len(s2),[]
    #if m>n: m,n,s1,s2 = n,m,s2,s1
    accum = 0
    for i in range(0,m):
        if s1[i] == '-':
            s2 = s2[0:i]+['-']+s2[i+1:]
            accum+=1
    path,cost = edit_graph(s1,s2,nn)
    #need to trouble shoot this because of index errors
    
    try: #convert this to a nested for loop?
        while m>0 or n>0:
            if path[m][n]=='M' or path[m][n]=='P':
                m,n,t = m-1,n-1,[s1[m-1]]+t
            elif path[m][n] == 'S':
                m,n,t = m-1,n-1,[s1[n-1]]+t
            elif path[m][n] == 'I':
                m,n,t = m,n-1, ['-']+t
            else:
                m,n = m-1,n
    except IndexError:
        print "IndexError m=%s, n=%s"%(m,n),s1,s2 
        t = s1
        m = max(len(s1),len(s2))-len(s1)
        for i in range(0,m): t = ['-']+t
    return t,cost

#tests si for NN sj using array nn
def nn_rank(si,sj,nn):
    if si!='-':
        if nn.ndim==1:   k,n = nn.shape[0],nn[si]
        elif nn.ndim==2: k,n = nn.shape[1],nn[si,]
        else: k,n = 0,[] #sets k value, 0 for no k value, no NN present
        if sj in n: return np.where(n==sj)[0][0]+1 #ascending rank of nn 1 to k
    return 0  

#nn based weighting scores
def w(t,k): #M=Match, I=Insert, D=Delete, S=Sub, P=Partial NN
    c = {'M':lambda x:0,'I':lambda x:1,'D':lambda x:1,
         'S':lambda x:3, 'P':lambda x:0 }
    return c[t](k)
          
# Minimum Sum of Pairs Score with string index i
# uses an upper bound for the worste minSum as
# number of seq * longest sequence -> n*m
def min_sp(ss,a,nn):
    n = len(ss)
    m = max([len(i) for i in ss])
    d,r = np.zeros((n,n),dtype=float),np.zeros((n,n),dtype='bool')
    pairs = [(j,k) for j,k in it.combinations(range(0,n),2)]
    for j,k in pairs:
        x = edit_dist(ss[j],ss[k],nn)
        y = edit_dist(ss[j],ss[k][::-1],nn)+a #reversal and penalty
        if x<y: d[j][k] = x
        else:   d[j][k],r[j][k] = y,True
        d[k][j],r[k][j] = d[j][k],r[j][k] #symetric, so save time
    i = np.argmin([np.sum(d[:,j]) for j in range(0,n)])
    minSum = np.min([np.sum(d[:,j]) for j in range(0,n)])
    return minSum,i,d,r #r is which pairs are better flipped

def star(s,c,d,r,nn):
    n,accum,rs = len(s),0,[]
    for i in range(0,n): #align center to next closest from the original
        if r[i,c]:
            s[i],cost = edit(s[i][::-1],s[c],nn)
            r[i,c],r[c,i] = 0,0
        else:   s[i],cost = edit(s[i],s[c],nn)
        accum+=cost
        for j in range(0,i+1): #now align all others to s[c]
            if i != j:
                if r[c,j]:
                    s[j],cost = edit(s[j][::-1],s[c],nn)
                    r[c,j],r[j,c] = 0,0
                else:   s[j],cost = edit(s[j],s[c],nn)                        
                accum+=cost
    return s,accum

#run the test code here, this is a dual path tester
L = [[1,1,1,3,3,3,5,5,5,7,7,7,9,9,9],
     [9,1,9,7,7,7,5,5,5,3,3,3,1,1,1],
     [9,9,7,7,7,5,5,3,3,1,1],
     [1,1,1,4,4,9,9,9],
     [8,9,9,6,7,0,0],
     [0,0,0,2,2,2,4,4,4,6,6,6,8,8,8],
     [0,0,0,2,2,2,4,4,6,6,6,8],
     [8,8,8,6,4,2,2,2]]

#L = [[0,0,0,2,2,2],[0,0]]
#spatial pos for ids 0,1,2,3,4,5,6,7,8,9 to do nn on
pos = np.asarray([[0,0],[0,1], #0 and 1 are nn
                  [2,0],[2,1], #2 and 3 are nn
                  [4,0],[4,1], #4 and 5 are nn
                  [6,0],[6,1], #6 and 7 are nn
                  [8,0],[8,1]],#8 and 9 are nn
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
    
start = time.time()

nn = distance.ann(pos,2)[1][:,1:]
#nn = np.zeros(nn.shape,dtype='u2')-1
print("vertex nn:")
print(nn.T)

for i in range(0,1):
    print("computing min sp")
    T,I,D,R = min_sp(L,0,nn) #ss,a,nn
    S = copy.deepcopy(L)
    print("done\ncomputing center star")
    L,cost = star(L,I,D,R,nn)
stop = time.time()

print('min star cost:%s\ntotal cost:%s'%(T,cost))
star = ''.join([str(i).ljust(s+1) for i in S[I]])
print('min star used: '+star)
for r in L:
    for i in r:
        l = len(str(i))
        print str(i).ljust(s+1),
    print('')
print('time is %s ms'%((stop-start)*1000.0))
