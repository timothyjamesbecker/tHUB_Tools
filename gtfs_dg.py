#gtfs_dg_v2 v 0.5, 04/16/2014-07/06/2014
#Timothy Becker, UCONN/SOE/CSE

import re
import httplib
import copy
import datetime
import numpy as np
import itertools as it
import cPickle as pickle
import scipy.sparse as sparse
import matplotlib.pylab as plt
import file_tools
import align
import distance
import similarity

class G:
    def __init__(self,gtfs_path,g_path):
        self.V,self.E,self.AE,self.RE,self.paths,self.routes = {},{},{},{},{},{}
        self.gtfs,self.VI,self.IV,self.EI,self.IE,self.AM,self.BM = {},{},{},{},{},[],[]
        path,pkl = gtfs_path,g_path
        #look for a prexisting dg from the same .zip file
        #we assume here that when a new GTFS is generated
        #it will get a new name and therefore allow us to precompute G
        try:
            print('Loading Serialized Directed Graph: '+pkl)
            pkl_file = open(pkl,'rb')
            data = pickle.load(pkl_file)
            self.V = data['V']
            self.E = data['E']
            self.AE = data['AE']
            self.RE = data['RE']
            self.paths = data['paths'] #fix up import/ export later...
            self.routes = data['routes']
            self.gtfs = data['gtfs']
            self.VI = data['VI']
            self.IV = data['IV']
            self.IE = data['IE']
            self.EI = data['EI']
            #self.AM = data['AM']
            #self.BM = data['BM']
            pkl_file.close()
            print('Load Complete')
        except IOError: #didn't find a preprossed data set, so make one
            print('Error Reading Serialization: '+pkl)
            print('Attempting Rebuild using '+path)
            self.build_V(path)
            self.build_E()
            pkl_out = open(pkl, 'wb')
            pickle.dump(dict(V=self.V,E=self.E,AE=self.AE,RE=self.RE,paths=self.paths,
                             routes=self.routes,gtfs=self.gtfs,IV=self.IV,VI=self.VI,
                             IE=self.IE,EI=self.EI),#AM=self.AM,BM=self.BM),
                        pkl_out, pickle.HIGHEST_PROTOCOL)
            pkl_out.close()
            print('Rebuild Complete for : %s'%pkl)
            print('Done')  
        
    def build_V(self,path): #TO DO TYPE CONVERSIONS
        ft = file_tools.File_Tools()
        PKS = {'trips':'trip_id','routes':'route_id','shapes':'shape_id',
               'stop_times':'trip_id'+'@'+'stop_id','stops':'stop_id',
               'calendar':'service_id','calendar_dates':'service_id'}
        #start by building V
        uncompressed = ft.read_zip_csv(path,[])
        gtfs = {}
        for raw in uncompressed:
            pathname = raw[0] #grab file path _ name and trim it out
            name = max([s if re.search(s,pathname)!=None else '' for s in PKS.keys()])
            if name == '': name = 'skipping file...'
            print("\nProccessing file: %s as key: %s" %(pathname,name))
            if name in PKS.keys():
                fields = raw[1]
                print("Fields located: %s" %fields)
                raw,PK,m = raw[2:],PKS[name],{}
                for i in range(0,len(raw)):
                    r = {fields[j]:raw[i][j] for j in range(0,len(raw[i]))}
                    p = re.split('\@',PK)
                    if len(p)==1 and r.has_key(PK): m.update({r.pop(PK):r})
                    elif len(p)>1: #for stop_times with two PKs
                        v = []     #keeps
                        for j in p: v.append(r.pop(j))
                        m.update({'@'.join(v):r})              
                gtfs[name] = m 
        #safety check for gtfs
        print("\nGTFS has the following keys:")
        print(gtfs.keys())
        self.gtfs = gtfs
        #construct each vertex by stop_id
        for k in gtfs['stops'].keys():
            m = gtfs['stops'][k]
            if k!='PK': #don't search fips, NN stuff for now...
                self.V[k] = {'pos':[float(m['stop_lat']),float(m['stop_lon'])],
                             'name':m['stop_name'],'fips':'','trips':[],
                             'count':0,'inout':[0,0],'deg':[0,0]}
        #insert all trip/stop_time pairs into vertex
        for t in gtfs['stop_times'].keys(): #do this in sorted/original order?
            trip_id,stop_id = tuple(t.split('@'))
            m = gtfs['stop_times'][t]
            try: seq = int(m['stop_sequence'])
            except ValueError: print('Sequence %s not Readible...'%m['stop_sequence'])
            try: dist = float(m['shape_dist_traveled'])
            except ValueError: dist = 0.0 #some values have 0 dist defined as ''
            if self.paths.has_key(trip_id): #this is to construct edges
                self.paths[trip_id].append([stop_id,dist,seq])
            else: self.paths[trip_id] = [[stop_id,dist,seq]]
            t0 = [int(i) for i in m['arrival_time'].split(':')]             
            try:                                 
                time = datetime.timedelta(hours=t0[0],minutes=t0[1],seconds=t0[2]) 
                self.V[stop_id]['trips'].append([time,trip_id])
            except TypeError: print(t0)
            
        #for each vertex sort trip/time pairs by acending time
        for k in self.V.keys():
            self.V[k]['trips'] = sorted(self.V[k]['trips'], key=lambda x: x[0])
            self.V[k]['count'] = len(self.V[k]['trips'])
            
    def build_E(self): #TO DO TYPE CONVERSIONS
        #for each edge in each path
        for k in self.paths.keys():
            path = self.paths[k]
            path = [[i[0],i[1]] for i in sorted(path,key=lambda x: x[2])]
            for i in range(0,(len(path)-1)):        #now we have a sorted path
                P,K = path[i][0],path[i+1][0]       #each i,j pair in the path
                PK = P+'@'+K
                dist = abs(path[i][1]-path[i+1][1]) #abs distance
                if self.E.has_key(PK): #mean for dist
                    self.E[PK]['dist'] += dist
                    self.E[PK]['count'] += 1
                else: self.E[PK] = {'count':1,'dist':dist ,'mean':0.0}
                self.V[K]['inout'][0] += 1 #in  degree +1
                self.V[P]['inout'][1] += 1 #out degree +1
            dists = [0.0]+list(np.diff([i[1] for i in path]))
            for i in range(0,len(path)): path[i][1] = dists[i]
            self.paths[k] = path
        #fix the average edge dist
        for k in self.E.keys():
            self.E[k]['mean'] = self.E[k]['dist']/self.E[k]['count']
            
        for k in self.gtfs['trips'].keys():
            m = self.gtfs['trips'][k]
            if self.routes.has_key(m['route_id']):
                self.routes[m['route_id']].append(k)
            else: self.routes[m['route_id']] = [k]
        
        #additional meta data here..
        ks,n = self.E.keys(),len(self.E.keys())
        self.EI = {ks[i]:i for i in range(0,n)} #index of edges
        self.IE = {i:ks[i] for i in range(0,n)} #keys of edges
        #additional meta data here..
        #reform E to e[i][j] adjacency and reverse adjaceny list form
        for k in self.E.keys():
            P,K = tuple(k.split('@'))
            if self.AE.has_key(P):
                if not self.AE.has_key(K): self.AE[P][K] = self.E[k]
            else: self.AE[P] = {K:self.E[k]}
            if self.RE.has_key(K):
                if not self.RE.has_key(P): self.RE[K][P] = self.E[k]
            else: self.RE[K] = {P:self.E[k]}
            
        #calculate degrees    
        for k in self.V.keys():
            try: in_deg = len(self.RE[k])
            except KeyError: in_deg = 0
            try: out_deg = len(self.AE[k])
            except KeyError: out_deg = 0
            self.V[k]['deg'] = [in_deg,out_deg]
        
        #build the adjacency matrix AM
        ks,n = self.V.keys(),len(self.V.keys())
        self.VI = {ks[i]:i for i in range(0,n)} #indecies of verticies
        self.IV = {i:ks[i] for i in range(0,n)} #keys of vertecies
        self.AM = np.zeros((n,n),dtype='u2')
        self.BM = np.zeros((n,n),dtype='bool')        
        for p in self.V.keys():
            for k in self.AE[p].keys():
                pk = '@'.join([p,k])
                self.AM[self.VI[p]][self.VI[k]] = self.E[pk]['count']
                self.BM[self.VI[p]][self.VI[k]] = True
        self.AM = sparse.csr_matrix(self.AM)
        self.BM = sparse.csr_matrix(self.BM)    
    
    #accessors of data elements within g.V
    def get_pos(self,V):
        xy = []
        for v in V: xy += [self.V[self.IV[v]]['pos']]
        return np.asarray(xy,dtype=float)
            
    
    #build and return the subgraphs GS given the path set ps
    #should refactor this as route2subgraph or something
    def subgraph(self,ps): #list of strings that are the path keys
        GS = {}
        if type(ps) != list: ps = list(ps)
        for p in ps: #each string is a key
            V,E = [],[]
            last = self.paths[p][0][0] #string key
            V.append(self.VI[last]) #get int index
            for x in range(1,len(self.paths[p])): #each path is a sequence
                new = self.paths[p][x][0] #vertex string
                V.append(self.VI[new])
                PK = '@'.join([last,new])
                E.append(self.EI[PK])
                last = new
            GS[p] = {'V':V,'E':E}
        return GS

    def subgraph_unique(self,GS,by):
        U = [GS[k][by] for k in GS]               #unique vertices
        U = list(set([j for i in U for j in i]))  #hashed flattened list
        U = sorted(U)                             #sorted and mapped
        ki = {U[i]:i for i in range(0,len(U))}    #map forward and
        ik = {i:U[i] for i in range(0,len(U))}    #in reverse
        return {'ki':ki,'ik':ik}

    def subgraph_sequence(self,GS,by,U):
        ki,ik = U['ki'],U['ik']
        L,J = [],[]             #L is the unique mapped, J is the original
        m = max([len(GS[k][by]) for k in GS]) #longest sequence
        for k in GS:
            J.append(GS[k][by])
            L.append([ki[i] for i in GS[k][by]])
        return L,J
    
    def sequence_vertex_merge(self,S,U,a):
        ki,ik = U['ki'],U['ik']
        #if mutual nn and disjoint in GS
        #do the fast a-nn nn should be set to the sorted key based ki,ik tables
        pos = self.get_pos(ki.keys())                     #resolve spatial positions
        if a>0: nn = distance.ann(pos,a)[1][:,1:] #do a in-route approximate a-nn
        else:   nn = np.zeros((0,),dtype='float') #this can be used to short curcuit nn use
        #build frequencies of transistions
        F,c,e = simularity.edge_entropy(S,'shannon')
        #tally up in and out edges
        in_f,out_f = {},{}
        for K in F:
            p,k = [int(i) for i in K.split('@')]
            if in_f.has_key(p): in_f[p]+=F[K]
            else: in_f[p]=F[K]
            if out_f.has_key(k): out_f[k]+=F[K]
            else: out_f[k]=F[K]
        merge = {}
        pairs = [(j,k) for j,k in it.combinations(range(0,len(ki)),2)]
        for j,k in pairs:
            is_mutual_nn = nn[j]==k and nn[k]==j #check for mutal nn
            #check for connectivity
            jk = '@'.join([str(j),str(k)])
            kj = '@'.join([str(k),str(j)])
            not_connected = not (F.has_key(jk) or F.has_key(kj))
            if is_mutual_nn and not_connected:
                x,y = 0,0 #add these for now could do more with flow
                if in_f.has_key(j): x += in_f[j]
                if in_f.has_key(k): y += in_f[k]
                if out_f.has_key(j): x += out_f[j]
                if out_f.has_key(k): y += out_f[k]
                if x<y: merge[j]=k
                else:   merge[k]=j
        #now loop through the sequence set and if any position 
        #needs a merge operation, apply the merge:  A[i][j] = merge[k]
        A = copy.deepcopy(S)
        for i in range(0,len(A)):
            for j in range(0,len(A[i])):
                if merge.has_key(A[i][j]):
                    A[i][j] = merge[A[i][j]]
        return {'F':F,'in':in_f,'out':out_f,'merge':merge, 'S':A}
            
    #do a pairwise comparison on all unique v or e and return d,r matricies
    def sequence_simularity(self,S,rp):
        return simularity.partition_fwd_rev(S,rp)
        
    
    def sequence_median(self,S,p):
        return simularity.all_median(S,p)
    
    #def sequence_align(self):
        
    
    #cstar alignment
    def subgraph_align(self,GS,by,method,a,w,rp):
        U = [GS[k][by] for k in GS]               #unique vertices
        U = list(set([j for i in U for j in i]))  #hashed flattened list
        U = sorted(U)                             #sorted and mapped
        ki = {U[i]:i for i in range(0,len(U))}    #map forward and
        ik = {i:U[i] for i in range(0,len(U))}    #in reverse
        
        #set up params
        pos = self.get_pos(U)                     #resolve spatial positions
        if a>0: nn = distance.ann(pos,a)[1][:,1:] #do a in-route approximate a-nn
        else:   nn = np.zeros((0,),dtype='float')
        print("vertex nn:")
        print(nn.T[0])
        A = align.Align(w,rp,nn,a)        
        
        L,J = [],[]             #L is the original vertice to IV mappings
        n = len(GS.keys())      #J is the uniquely mapped indecies
        m = max([len(GS[k][by]) for k in GS]) #longest sequence
        for k in GS:
            J.append(GS[k][by])
            L.append([ki[i] for i in GS[k][by]])
        
        s = max([max([len(str(J[i][j])) for j in range(0,len(J[i]))]) for i in range(0,n)])
        if method=='cstar':
            S = copy.deepcopy(J)
            print("Done\nComputing Alignment")
            A.pair(L,'cstar')
            S1 = []
            for i in A.s:
                s = []
                for j in i:
                   if j=='-': s+=[j]
                   else:      s+=[ik[j]]
                S1+=[s]
            print('total cost:%s'%A.cost)
            return S,S1,A.t,A.c,A.d
        elif method=='rand':
            S = copy.deepcopy(J)
            print("Done\nComputing Alignment")
            A.pair(L,'rand')
            S1 = []
            for i in A.s:
                s = []
                for j in i:
                   if j=='-': s+=[j]
                   else:      s+=[ik[j]]
                S1+=[s]
            print('total cost:%s'%A.cost)
            return S,S1,A.t,A.c,A.d
        else:
            return GS,GS,1,0,np.zeros((n,n),dtype=float)
        
    
    def alignment_consensus(self,A,T):
        T,T0,P,K,pi,ip,ki,ik = T #unpack transitions and indexes
        n = len(A)
        m = len(A[0])
        PWM,C0 = {i:{} for i in range(0,m)},{i:'-' for i in range(0,m)}
        for i in range(0,n):
            m = len(A[i])
            for j in range(0,m): #scan one sequence
                if PWM[j].has_key(A[i][j]): PWM[j][A[i][j]]+=1
                else: PWM[j][A[i][j]] = 1       
        #trim some of the '-' chars
        for k in PWM.keys():
            m = len(PWM[k].keys())
            #if m>1 and PWM[k].has_key('-'): PWM[k].pop('-')
            n,b = sum(PWM[k].values()),-1.0
            for j in PWM[k].keys():
                PWM[k][j] = PWM[k][j]/(n*1.0)
                if PWM[k][j] > b: b,C0[k] = PWM[k][j],j #maximum p value
        C0,C = list(C0.values()),{}
        #inital draw from T0
        for i in range(0,len(C0)-1):
            if i == 0 or C0[i]=='-' or C0[i+1]=='-': boost = T0[i]
            else: boost = T[pi[C0[i]],ki[C0[i+1]]]
            if PWM[i][C0[i]]+boost>0.5 and C0[i]!='-' and C0[i] not in C.values(): C[i] = C0[i]
            #if C0[i]!='-' and C0[i] not in C.values(): C[i] = C0[i]
        return PWM,C
                        
    def subgraph_transition(self,GS,by):
        L,M,P,K = [],{},{},{}
        n = len(GS.keys())    #total length
        for k in GS: L.append(GS[k][by]) #L is the data set
        for x in range(0,n):
            m = len(GS[GS.keys()[x]][by])
            for y in range(0,m-1):
                i,j = L[x][y],L[x][y+1] #sequence links
                ij = '@'.join([str(i),str(j)])
                if P.has_key(i): P[i]+=1
                else: P[i]=1
                if K.has_key(j): K[j]+=1
                else: K[j]=1
                if M.has_key(ij): M[ij]+=1
                else: M[ij]=1
        p = P.keys() #starting links
        k = K.keys() #unique points
        U = sorted(list(set(P.keys()).union(set(K.keys()))))
        u = len(U)
        m = M.keys() #transistions
        pi = {p[i]:i for i in range(0,len(p))}
        ip = {i:p[i] for i in range(0,len(p))}
        ki = {k[i]:i for i in range(0,len(k))}
        ik = {i:k[i] for i in range(0,len(k))}
        #build the transition matrix
        alpha = 0.0001 #psuedo count corrector
        T = np.zeros((u,u),dtype=float)+alpha/10
        for xy in M:
            x,y = tuple(xy.split('@'))
            x,y = int(x),int(y)
            T[pi[x],ki[y]] = M[xy]/(P[x]+alpha)
        #correct transistion so they sum to 1.0  
        for i in range(0,T.shape[0]):
            s = np.sum(T[i,:])
            T[i,:] = T[i,:]/(s+alpha/10000)
            if s < alpha: T[i,:] = [1/(u*1.0) for j in T[i,:]]
                
        T0 = np.zeros((u,),dtype=float)
        for i in range(0,len(p)):
            T0[i] = P[p[i]]/(u*1.0) #basic frequencies
        return T,T0,P,K,pi,ip,ki,ik
        
    def alignment_print(self,A):
        s = max([max([len(str(A[i][j])) for j in range(0,len(A[i]))]) for i in range(0,len(A))])
        for r in A:
            for i in r:
                l = len(str(i))
                print str(i).ljust(s+1),
            print('\n')
            
    #def merge_aligned_subgraphs(self,GS):

    def subgraph_plot(self,GS):
        for g in GS.keys():
            for i in GS[g]['V']:
                c,a,s = 'r',0.5,5
                k = self.IV[i]
                plt.plot(self.V[k]['pos'][0],self.V[k]['pos'][1],marker='.',color=c,
                         markersize=s,alpha=a)
            for i in GS[g]['E']:
                k = self.IE[i]
                P,K = tuple(k.split('@'))
                p1 = {'x':self.V[P]['pos'][0],'y':self.V[P]['pos'][1]}
                p2 = {'x':self.V[K]['pos'][0],'y':self.V[K]['pos'][1]}
                dx,dy = p2['x']-p1['x'],p2['y']-p1['y']
                dist = pow(pow(dx,2)+pow(dy,2),0.5)
                a_w = dist/10
                e_w = dist
                a = 0.01
                plt.arrow(p1['x'],p1['y'],dx,dy,fc="k",ec="k",alpha=a, lw=e_w,
                          head_width=a_w, head_length=a_w,length_includes_head=True)
        #plt.show()
                          
    def consensus_plot(self,PWM,C):
        x,y = [],[]
        C0,j = C.values(),0
        for i in C0:
            if i!='-':
                plt.plot(self.V[self.IV[i]]['pos'][0],
                         self.V[self.IV[i]]['pos'][1],color='y',
                         marker='.',markersize=20,alpha=0.75)
                x += [self.V[self.IV[i]]['pos'][0]]
                y += [self.V[self.IV[i]]['pos'][1]]
            j+=1
        x,y = np.asarray(x),np.asarray(y)
        plt.plot(x,y,color='y',lw=2.0,alpha=0.5)
        plt.show()
    
    def median_plot(self,M,c):
        x,y = [],[]
        C0,j = M,0
        for i in C0:
            if i!='-':
                plt.plot(self.V[self.IV[i]]['pos'][0],
                         self.V[self.IV[i]]['pos'][1],color=c,
                         marker='.',markersize=20,alpha=0.5)
                x += [self.V[self.IV[i]]['pos'][0]]
                y += [self.V[self.IV[i]]['pos'][1]]
            j+=1
        x,y = np.asarray(x),np.asarray(y)
        plt.plot(x,y,color=c,lw=2.0,alpha=0.25)
        plt.show()
    
    def plot(self):
        #draw vertecies
        L = [self.V[k]['inout'][0]-self.V[k]['inout'][1] for k in self.V]
        max_deg,min_deg,ave_deg = max(L),min(L),np.mean(L)
        for k in self.V.keys():
            deg = self.V[k]['inout'][0]-self.V[k]['inout'][1]
            if(np.sign(deg)>0):   #sink more in than out
               c,a,s = 'r',min(1.0,max(0.4,deg/max_deg)),20.0
            elif(np.sign(deg)<0): #source more out than in
                c,a,s = 'g',min(1.0,max(0.4,deg/min_deg)),20.0
            else:
                c,a,s = 'b',min(0.4,max(0.1,deg/(ave_deg+1))),2.0
            plt.plot(self.V[k]['pos'][0],self.V[k]['pos'][1],marker='.',color=c,
                    markersize=s,alpha=a)

        counts = [self.E[k]['count'] for k in self.E.keys()]        
        max_c,min_c,ave_c = max(counts),min(counts),np.mean(counts)
        means = [self.E[k]['mean'] for k in self.E.keys()]        
        max_m,min_m,ave_m = max(means),min(means),np.mean(means)
        for k in self.E.keys():
            a_w,e_w = 0.008,0.1
            a = min(0.4,max(0.01,self.E[k]['mean']/(max_m*ave_m)))
            P,K = tuple(k.split('@'))
            p1 = {'x':self.V[P]['pos'][0],'y':self.V[P]['pos'][1]}
            p2 = {'x':self.V[K]['pos'][0],'y':self.V[K]['pos'][1]}
            dx,dy = p2['x']-p1['x'],p2['y']-p1['y']
            plt.arrow(p1['x'],p1['y'],dx,dy,fc="k",ec="k",alpha=a, lw=e_w,
                      head_width=a_w, head_length=a_w,length_includes_head=True)
        plt.show()
    
    #is a given edge(by key) symetric in the super graph
    def is_symetric(self,PK): #if for some edge e(p,k), there exists e(k,p)
        pk = list(PK.split('@'))
        KP = '@'.join([pk[1],pk[0]])
        if self.E.has_key(PK) and self.E.has_key(KP): return True
        else: return False
    
    def sort(self,by,rev):
        if by=='inout_delta':
            return self.__sort_inout_delta__(rev)
        elif by=='in':
            return self.__sort_in__(rev)
        elif by=='out':
            return self.__out_delta__(rev)
        elif by=='degree_delta':
            return self.__sort_degree_delta__(rev)
        elif by=='indegree':
            return self.__sort_indegree__(rev)
        elif by=='outdegree':
            return self.__sort_outdegree__(rev)
        elif by=='distance':
            return self.__sort_distance__(rev)
        elif by=='count':
            return self.__sort_count__(rev)
        elif by=='mean':
            return self.__sort_mean__(rev)
    
    def __sort_inout_delta__(self,rev):
        ks = self.V.keys()
        L = [[k,(self.V[k]['inout'][0]-self.V[k]['inout'][1])] for k in ks]
        L = sorted(L,key=lambda x: x[1],reverse=rev)
        return L
    
    def __sort_in__(self,rev):
        ks = self.V.keys()
        L = [[k,self.V[k]['inout'][0]] for k in ks]
        L = sorted(L,key=lambda x: x[1],reverse=rev)
        return L
    
    def __sort_out__(self,rev):
        ks = self.V.keys()
        L = [[k,self.V[k]['inout'][1]] for k in ks]
        L = sorted(L,key=lambda x: x[1],reverse=rev)
        return L
    
    def __sort_degree_delta__(self,rev):
        ks = self.V.keys()
        L = [[k,(self.V[k]['deg'][0]-self.V[k]['deg'][1])] for k in ks]
        L = sorted(L,key=lambda x: x[1],reverse=rev)
        return L
    
    def __sort_indegree__(self,rev):
        ks = self.V.keys()
        L = [[k,self.V[k]['deg'][0]] for k in ks]
        L = sorted(L,key=lambda x: x[1],reverse=rev)
        return L
    
    def __sort_outdegree__(self,rev):
        ks = self.V.keys()
        L = [[k,self.V[k]['deg'][1]] for k in ks]
        L = sorted(L,key=lambda x: x[1],reverse=rev)
        return L
    
    def __sort_distance__(self,rev):
        ks = self.E.keys()
        L = [[k,self.E[k]['dist']] for k in ks]
        L = sorted(L,key=lambda x: x[1],reverse=rev)
        return L
        
    def __sort_count__(self,rev):
        ks = self.E.keys()
        L = [[k,self.E[k]['count']] for k in ks]
        L = sorted(L,key=lambda x: x[1],reverse=rev)
        return L
    
    def __sort_mean__(self,rev):
        ks = self.E.keys()
        L = [[k,self.E[k]['mean']] for k in ks]
        L = sorted(L,key=lambda x: x[1],reverse=rev)
        return L
    
    
        
    #def update_g(self,path):    
    #def get_all_V_fips(self):
    #    for k in self.V.keys():
    #        V[k][]
    
    #def get_all_V_nn(self):
    
    def getfips(self,lat,lon): #use the census fips API
        conn = httplib.HTTPConnection('data.fcc.gov')
        conn.request('GET', '/api/block/find?latitude='+str(lat)+
                     '&longitude='+str(lon)+'&showall=false') #change to true for borders
        r,xml,block = conn.getresponse(),'',''
        if r.status==200 and r.reason=='OK': xml = r.read()
        conn.close()
        tag = re.search('<Block FIPS="',xml)
        xml = re.split('"/>',xml[tag.end():])[0]
        return xml
