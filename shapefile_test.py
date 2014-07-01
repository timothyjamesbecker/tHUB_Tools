import shapefile
# Make a point shapefile
w = shapefile.Writer(shapefile.POINT)
w.point(90.3, 30)
w.point(92, 40)
w.point(-122.4, 30)
w.point(-90, 35.1)
w.field('FIRST_FLD')
w.field('SECOND_FLD','C','40')
w.record('First','Point')
w.record('Second','Point')
w.record('Third','Point')
w.record('Fourth','Point')
w.save('../point')
# Create a polygon shapefile
w = shapefile.Writer(shapefile.POLYGON)
w.poly(parts=[[[1,5],[5,5],[5,1],[3,3],[1,1]]])
w.field('FIRST_FLD','C','40')
w.field('SECOND_FLD','C','40')
w.record('First','Polygon')
w.save('../polygon')

#Create a polyline shapefile
w = shapefile.Writer(shapefile.POLYLINE)
lineParts = []
lineParts.append([[1,5],[5,5],[6,6],[7,7]])
w.field('FIELD','C','40')
w.line(parts=lineParts)
w.record('First','Polyline')
w.save('../polyline')