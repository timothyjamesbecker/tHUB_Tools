#gtfs_dg_v1 v 0.1, 04/16/2013-06/28/2013
#Timothy Becker, UCONN/SOE/CSE
import time
import numpy as np
import gtfs_dg as dg
import distance
import simularity

base = 'HARTFORD'
path  = '../DATA_GTFS/'+base+'.zip'
g_path  = '../DATA_GTFS/'+base+'.zip.G.pkl'
g = dg.G(path,g_path)
#g.plot()

x = ['1221']#, '1205', '1224', '1221','1222','1205']#, '1222', '1221', '1220', '1205', '1204', '1952', '1206', '1201', '1200', '1203', '1228', '3166', '1223', '4477', '4476', '1199', '4828', '1191', '4827', '4536', '1192', '1195', '1194', '1197', '1196', '1402', '2683', '1212', '1213', '1210', '1211', '1217', '1214', '1215', '1219', '1229', '1934', '1202', '4509', '4508', '1190', '1188', '1189', '1186', '1187', '1184', '1185', '1182', '1183', '1180', '1181', '4826', '4535', '1193']
t = []
for k in x:
    #align one route at a time
    GS = g.subgraph(g.routes[k])
    start = time.time()
    T = g.subgraph_transition(GS,'V')
    #params
    w = {'M':lambda x:0,'I':lambda x:1,'D':lambda x:1,
         'S':lambda x:1, 'P':lambda x:0.1 }
    rp = 1
    #X,A,C,I,D = g.subgraph_align(GS,'V','cstar',1,w,rp)
    #PWM,C = g.alignment_consensus(A,T)
    stop = time.time()
    #print("original sequences:")
    #g.alignment_print(X)
    #print("aligned sequences:")
    #g.alignment_print(A)
    t+=[(stop-start)]
    print('Total Python Edit Distance Method Time was %s seconds\n'%(t[-1]))
    #new routines
    start = time.time()
    U = g.subgraph_unique(GS,'V')
    L,J = g.subgraph_sequence(GS,'V',U)
    p = g.sequence_simularity(L,1)
    print('finding medians...')
    m = g.sequence_median(L,p)
    ki,ik = U['ki'],U['ik']
    med = {'all':[ik[i] for i in m['all']],
           '>':[ik[i] for i in m['>']],
           '<':[ik[i] for i in m['<']]}
    stop = time.time()
    t+=[(stop-start)]
    print('Total Levenshtein Greedy Median Time was %s seconds\n'%(t[-1]))
    g.subgraph_plot(GS)
    #g.consensus_plot(PWM,C)
    g.median_plot(med['<'],(0.0,0.0,1.0,1.0))

#full workflow...
#[1] non-connected mutual-nn vertex merge
#[2] pairwise levenshtein edit distance and reversal paritioning
#[3] AIC clustering on the edit distance -> yeilds a tree
#[4] use the spatial data with the tree level for clusters


"""
PK = g.V.keys()
Q = [g.V[k]['pos'] for k in PK]
P = np.asarray(Q)
k = 10 #k-nearest neighbors
m = 1

print("Starting NN comparison")
start = time.time()
for i in range(0,m):
    D = d.alldist(Q,'karney')
    nn = d.knn(D,k) #l2 ~175x faster than karney
stop = time.time()
et = stop-start
print("Exact NN %s seconds"%et)

start = time.time()
for i in range(0,m):
    ann = d.ann(P,k) # ~600x faster than exact brute force
stop = time.time()
at = stop-start
print("ANN %s seconds"%at)

diff = np.zeros((D.shape[0],),dtype=float)
for i in range(0,D.shape[0]):
    diff[i] = 1.0-len(set(nn[i,])-set(ann[1][i,]))/(k*1.0)
print("ANN acuracy = %s"%np.mean(diff))
print("ANN speedup = %sx"%int(et/at))
"""   