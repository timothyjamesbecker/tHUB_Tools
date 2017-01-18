#distance functions and NN search  05/21/2014
#Timothy Becker, UCONN/SOE/CSE
import time
import numpy as np
import itertools as it
from scipy import spatial
import geographiclib.geodesic as geo

def haversine(p1,p2): #returns meters
    lat1,lat2,lon1,lon2 = p1[0],p2[0],p1[1],p2[1]
    x = pow(np.sin((lat2-lat1)/2),2)+  \
        np.cos(lat1)*np.cos(lat2)*     \
        pow(np.sin((lon2-lon1)/2),2)
    return 2*6378137*np.arctan2(np.sqrt(x),np.sqrt(1-x))/75.10928613284344

def lawofcosines(p1,p2): #returns meters
    lat1,lat2,lon1,lon2 = p1[0],p2[0],p1[1],p2[1]                  
    return 6378137*np.arccos(np.sin(lat1)*np.sin(lat2)+           \
                     np.cos(lat1)*np.cos(lat2)*np.cos(lon2-lon1))/75.10928613284344  

def equirectangular(p1,p2):
    lat1,lat2,lon1,lon2 = p1[0],p2[0],p1[1],p2[1]                      
    return 6378137*np.sqrt((pow((lat2-lat1)*np.cos((lat1+lat2)/2),2)+ \
                            pow((lon2-lon1),2)))/75.10928613284344
                            
#Nick Lownes implementation
def vincenty(p1,p2):
    a,b,f = 6378137,6356752.314245,1/298.257223563
    lat1,lat2,lon1,lon2 = p1[0],p2[0],p1[1],p2[1] 
    U1 = np.arctan((1-f)*np.tan(np.radians(lat1)))
    U2 = np.arctan((1-f)*np.tan(np.radians(lat2)))
    sinU1,sinU2,cosU1,cosU2 = np.sin(U1),np.sin(U2),np.cos(U1),np.cos(U2)
    eps = 0.0000000000000001
    L = np.radians(lon2 - lon1)+2*eps
    lamb = [0,L]
    while ((np.abs(lamb[-1]) - np.abs(lamb[-1 - 1])) > eps):
        sinsig = np.sqrt(np.power((cosU2 * np.sin(lamb[-1])),2)+ \
                 np.power((cosU1 * sinU2 - sinU1 * cosU2 * np.cos(lamb[-1])),2))
        cossig = sinU1 * sinU2 + cosU1 * cosU2 * np.cos(lamb[-1])
        sigma = np.arctan2(sinsig, cossig)
        sinalph = (cosU1 * cosU2 * np.sin(lamb[-1]))/sinsig
        cos2alph = 1 - sinalph * sinalph
        cos2sigm = cossig - 2 * sinU1 * sinU2/cos2alph
        C = f/16 * cos2alph * (4 + f * (4 - 3 * cos2alph))
        lamb.append(L + (1-C) * f * sinalph * \
                    (sigma+C * sinsig * (cos2sigm + C * cossig * \
                    (-1 + 2 * cos2sigm * cos2sigm))))
    uu = cos2alph * (a * a - b * b)/(b * b)
    A = 1 + uu / 16384 * (4096 + uu * (-768 + uu * (320 - 175 * uu)))
    B = uu / 1024 * (256 + uu * (-128 + uu * (74 - 47 * uu)))
    delsig = B * sinsig * (cos2sigm + 1/4 * B * \
             (cossig * (-1 + 2 * cos2sigm*cos2sigm) - 1/6 * B * cos2sigm * \
             (-3 + 4 * sinsig*sinsig) * (-3 + 4 * cos2sigm*cos2sigm)))
    return (b * A * (sigma - delsig))

#karney Newtonian Convergence Method Wrapper
def karney(p1,p2):
    lat1,lat2,lon1,lon2 = p1[0],p2[0],p1[1],p2[1]
    return geo.Geodesic.WGS84.Inverse(p1[0],p1[1],p2[0],p2[1])

def L2(p1,p2): #returns L2 norm on lat/lon
    dlat,dlon = (p2[0]-p1[0]),(p2[1]-p1[1])
    return 84918.08840679418*pow(dlat*dlat+dlon*dlon,0.5)

def alldist(Q,t):
    d = {'haversine':lambda x,y:haversine(x,y),
         'lawofsin':lambda x,y:lawofcosines(x,y),
         'equirect':lambda x,y:equirectangular(x,y),
         'vincenty':lambda x,y:vincenty(x,y),
         'karney':lambda x,y:karney(x,y)['s12'],
         'l2': lambda x,y:L2(x,y)}
    n = len(Q) #number of points
    D = np.zeros((n,n),dtype=float)
    pairs = it.combinations(range(0,n),2)
    for i,j in pairs:
        D[i,j] = D[j,i] = d[t](Q[i],Q[j])
    return D

def knn(D,k):
    d = np.zeros((D.shape[0],k),dtype='u2')
    for i in range(0,D.shape[0]):
        d[i] = np.argsort(D[i,])[0:k]
    return d
    
#ANN wrapper
def ann(Q,k):
    kdt = spatial.cKDTree(Q,leafsize=20) #leafsize tunes KDT build time
    return kdt.query(Q,k=k+1,eps=0.0,p=2)  #p=2 => l2 norm

#takes the nn calculation and converts to
#an nxn redundant distance matrix for n vertecies
def ann2distance(nn):
    n = nn[0].shape[0] #get n
    d = np.zeros((n,n),dtype=float) #this will be the distance matrix
    for i in range(0,n):
        for j in range(0,n):
            d[i][nn[1][i][j]] = nn[0][i][j]
    return d
       
#def boundingbox(Q):
    #find a bounding box that includes all points in set Q
   
#some rampant testing code...
#L2 is ~400x faster than vincenty, ~175x faster than karney
"""
p1 = (41.767637, -72.700474)
p2 = (41.766765, -72.706853)

start = time.time()
for i in range(0,100000):
    v = karney(p1,p2)
stop = time.time()
print("Karney is %s , time=%s\n"%(karney(p1,p2),stop-start))

start = time.time()
for i in range(0,100000):
    v = L2(p1,p2)
stop = time.time()
print("L2 is %s , time=%s\n"%(L2(p1,p2),stop-start))
"""