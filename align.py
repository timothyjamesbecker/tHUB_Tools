#align for lists with arbitrary symbols seq v 0.4, 04/16/2014-07/11/2014
#Timothy Becker, UCONN/SOE/CSE

import copy
import numpy as np
import distance
import itertools as it
import time
import sys

class Align:
    def __init__(self,W,RP,NN,K):
        self.w = W    #wieght function for M,P,D,I,S
        self.rp = RP  #reversal penalty
        self.nn = NN  #nearest neighbor index matrix
        self.k = K    #weight parameter for NN to partial P

    # compute the edit graph between two strings using
    # the Wagner-Fisher Algorithm and the edit values:
    #M,P = Match|Partial, I = Insertion, D = Delete, S = Substitution
    def edit_graph(self,s1,s2):
        u,v = len(s1),len(s2)
        d = [[0 for col in range(v+1)] for row in range(u+1)]
        b = [['M' for col in range(v+1)] for row in range(u+1)]
        for i in range(0,u+1): d[i][0] = i
        for j in range(0,v+1): d[0][j] = j
        for j in range(1,v+1):
            for i in range(1,u+1):
                k = self.nn_rank(s1[i-1],s2[j-1]) #get nn rank
                min_w = 0==np.argmin([self.w['P'](k),self.w['I'](self.k),self.w['D'](self.k),self.w['S'](self.k)])
                if s1[i-1] == s2[j-1]:
                    d[i][j],b[i][j] = d[i-1][j-1]+self.w['M'](self.k), 'M'
                elif k>0 and min_w:
                    d[i][j],b[i][j] = d[i-1][j-1]+self.w['P'](self.k), 'P' 
                elif d[i-1][j] <= d[i][j-1] and d[i-1][j] <= d[i-1][j-1]:
                    d[i][j],b[i][j] = d[i-1][j]+  self.w['D'](self.k), 'D'
                elif d[i][j-1] <= d[i-1][j-1]:  
                    d[i][j],b[i][j] = d[i][j-1]+  self.w['I'](self.k), 'I'
                else:
                    d[i][j],b[i][j] = d[i-1][j-1]+self.w['S'](self.k), 'S'
        return b, d[u][v]

    # Wagner-Fisher Edit Distance Algorithm
    # from two strings s1,s2 computes the
    # min # of moves to make s1 into s2
    def edit_dist(self,s1,s2):
        u,v = len(s1),len(s2)
        d = np.zeros((u+1,v+1),dtype='float')
        #d = [[0 for col in range(v+1)] for row in range(u+1)]
        #for i in range(0,u+1): d[i][0] = i
        d[:,0] = np.asarray(range(0,u+1),dtype='float')
        #for j in range(0,v+1): d[0][j] = j
        d[0,:] = np.asarray(range(0,v+1),dtype='float')
        for j in range(1,v+1):
            for i in range(1,u+1):
                k = self.nn_rank(s1[i-1],s2[j-1]) #check nn rank for wieght
                if s1[i-1] == s2[j-1]: d[i,j] = d[i-1,j-1]
                elif k>0: d[i][j] = min(d[i-1,j-1]+self.w['P'](self.k),
                                        d[i-1,j]+  self.w['D'](self.k),
                                        d[i,j-1]+  self.w['I'](self.k),
                                        d[i-1,j-1]+self.w['S'](self.k))
                else:     d[i][j] = min(d[i-1,j]+  self.w['D'](self.k),
                                        d[i,j-1]+  self.w['I'](self.k),
                                        d[i-1,j-1]+self.w['S'](self.k))
        return d[u,v]

    # align s1 to s2
    def edit(self,s1,s2): #assumes that s2 is larger if there is difference
        m,n,t = len(s1),len(s2),[]
        #if m>n: m,n,s1,s2 = n,m,s2,s1
        accum = 0
        #for i in range(0,n):
        #    if s2[i] == '-': s1,accum = s1[0:i]+['-']+s1[i+1:],accum+1
        path,cost = self.edit_graph(s1,s2)
    
        try: #convert this to a nested for loop?
            while m>0 and n>0:
                if path[m][n]=='M' or path[m][n]=='P':
                    m,n,t = m-1,n-1,[s1[m-1]]+t
                elif path[m][n] == 'S':
                    m,n,t = m-1,n-1,[s1[n-1]]+t
                elif path[m][n] == 'I':
                    m,n,t = m,n-1,['-']+t
                else:
                    m,n = m-1,n
            for i in range(0,len(s1)-len(t))[::-1]: t += ['-']
        except IndexError:
            print "IndexError m=%s, n=%s"%(m,n),s1,s2 
            t = s1
            m = max(len(s1),len(s2))-len(s1)
            for i in range(0,m): t = ['-']+t
        return t,cost

    #tests si for NN sj using array nn
    def nn_rank(self,si,sj):
        if si!='-':
            if self.nn.ndim==1 and self.nn.shape[0]>0:
                k,n = self.nn.shape[0],self.nn[si]
            elif self.nn.ndim==2: 
                k,n = self.nn.shape[1],self.nn[si,]
            else: k,n = 0,[] #three dimensions or some other unknown input
            if sj in n: return np.where(n==sj)[0][0]+1 #ascending rank of nn 1 to k
        return 0  
 
    # Minimum Sum of Pairs Score with string index i
    # uses an upper bound for the worste minSum as
    # number of seq * longest sequence -> n*m
    def min_sp(self,ss):
        n,z = len(ss),0
        m = max([len(i) for i in ss])
        self.d,self.r = np.zeros((n,n),dtype=float),np.zeros((n,n),dtype='bool')
        pairs = [(j,k) for j,k in it.combinations(range(0,n),2)]
        print('Computing %s Score Pairs'%(n*(n-1)/2))
        for j,k in pairs:
            x = self.edit_dist(ss[j],ss[k])
            y = self.edit_dist(ss[j],ss[k][::-1])+self.rp #reversal and penalty
            if x<y: self.d[j][k] = x
            else:   self.d[j][k],self.r[j][k] = y,True
            self.d[k][j],self.r[k][j],z = self.d[j][k],self.r[j][k],z+1 #symetric, so save time
            if z%1000==0: print '.',
        self.c = np.argmin([np.sum(self.d[:,j]) for j in range(0,n)])
        self.t = np.min([np.sum(self.d[:,j]) for j in range(0,n)])

    def pair(self,s,method):
        if method=='cstar':
            self.min_sp(s)
            c,r,n,accum,rs = self.c,self.r,len(s),0,[]
        elif method=='rand':
            n,accum,rs = len(s),0,[]
            d,c,r = np.zeros((n,n),dtype=float),np.random.randint(0,len(s)-1),np.zeros((n,n),dtype='bool')
            self.d,self.c,self.r,self.t = d,c,r,0
        else:
            n,accum,rs = len(s),0,[]
            d,c,r = np.zeros((n,n),dtype=float),0,np.zeros((n,n),dtype='bool')
            self.d,self.c,self.r,self.t = d,c,r,0
        for i in range(0,n): #align center to next closest from the original
            if i != c:
                if r[i,c]:
                    if len(s[i])>len(s[c]):
                        s[c],cost = self.edit(s[i][::-1],s[c])
                    else:
                        s[i],cost = self.edit(s[c],s[i][::-1])
                    r[i,c],r[c,i] = 0,0
                else:
                    if len(s[i])>len(s[c]):
                        s[c],cost = self.edit(s[i],s[c])
                    else:
                        s[i],cost = self.edit(s[c],s[i])
                accum+=cost
            for j in range(0,i): #now align all others to s[c]
                if j != i and j != c:
                    if r[i,j]:
                        if len(s[j])>len(s[i]):
                            s[i],cost = self.edit(s[j][::-1],s[i])
                        else:
                            s[j],cost = self.edit(s[i],s[j][::-1])
                        r[i,j],r[j,i] = 0,0
                    else:
                        if len(s[j])>len(s[i]):
                            s[i],cost = self.edit(s[j],s[i])
                        else:
                            s[j],cost = self.edit(s[i],s[j])                        
                    accum+=cost
        self.s,self.cost = s,accum
