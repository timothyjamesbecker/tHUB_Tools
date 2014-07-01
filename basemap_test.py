import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
# Lambert Conformal Conic map.
m = Basemap(llcrnrlon=-100.0,llcrnrlat=0.0,urcrnrlon=-20.0,urcrnrlat=57.0,
            projection='lcc',lat_1=20.0,lat_2=40.0,lon_0=-60.0,
            resolution ='l',area_thresh=1000.0)
            
shape_path = './CTTRANSIT_GTFS_May_21_2013/HARTFORD_googleha_transit_May_21_2013/shapes'

# read shapefile.
shp_info = m.readshapefile(shape_path,'bustracks',drawbounds=False)
# find names of storms that reached Cat 4.
names = []
for shapedict in m.bus_info:
    print()
        
# draw coastlines, meridians and parallels.
#m.drawcoastlines()
#m.drawcountries()
#m.drawmapboundary(fill_color='#99ffff')
#m.fillcontinents(color='#cc9966',lake_color='#99ffff')
#m.drawparallels(np.arange(10,70,20),labels=[1,1,0,0])
#m.drawmeridians(np.arange(-100,0,20),labels=[0,0,0,1])
#plt.title('Hartford Bus Tracks')
#plt.show()