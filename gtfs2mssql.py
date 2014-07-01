#python script will connect to SQL server at fixed URL and port
#tHUB Project UCONN: http://www.thub.uconn.edu
#GTFS SQL Import Tool v 0.8
#Timothy Becker, Graduate Research Assistant

import csv
import os
import mssql
import file_tools

#forms MSSQL 2008R2 compatible INSERT STATEMENTS can be extended for queries
class GTFS2MSSQL(mssql.MSSQL): 
    #constructor
    def __init__(self,drv,srv,db,gtfs_zip): 
        mssql.MSSQL.__init__(self,drv,srv,db) #start up DB connection and bind to self.conn
        self.ft = file_tools.File_Tools()     #read compressed GTFS Files in .zip directory
        #GTFS input variables
        self.map = {'agency.txt':['GTFS_Agency','-1','name','url','null','null','null','null'],
                    'calendar.txt':['GTFS_Calendar','-1','0','0','0','0','0','0','0','20130101','20150101'],
                    'calendar_dates.txt':['GTFS_Calendar_Dates','-1','20130101','null'],
                    'routes.txt':['GTFS_Routes','-1','-1','null','null','null','null','null','null','null'],
                    'route_types.txt':['GTFS_Route_Types','-1','null'],
                    'trips.txt':['GTFS_Trips','-1','-1','-1','null','-1','-1','-1'],
                    'stops.txt':['GTFS_Stops','-1','null','name','0.0','0.0','zone','null','null','null'],
                    'stop_times.txt':['GTFS_Stop_Times','-1','00:00:00','00:00:01','-1','-1','null','null','null','0.0','0','0'],
                    'frequencies.txt':['GTFS_Frequencies','-1','00:00:01','1','null','null','null'],
                    'shapes.txt':['GTFS_Shapes','-1','0.0','0.0','-1','0.0'],
                    'transfers.txt':['GTFS_Transfers','-1','-1','null','null'],
                    'tranfer_types.txt':['GTFS_Transfer_Types','-1','null'],
                    'feed_info.txt':['GTFS_Feed_Info','name','url','null','null','null','20130101','21000101']
                    }
        self.map.keys().sort()
        #self.gtfs_names = list(set(self.map.keys()).intersection(set(os.listdir(gtfs_zip)))).sort()
        #self.gtfs_values = [self.ft.read(gtfs_dir+'\\'+s)[1:] for s in self.gtfs_names]
        
        self.gtfs_names, self.gtfs_values = [],[]
        uncompressed = self.ft.read_zip_csv(gtfs_zip,[])[1:]
        for s in self.map.keys():
            for name in uncompressed: #filename.txt = name[0], header = name[1]
                if s == name[0]:
                    print(name[0])
                    self.gtfs_names.append(name[0])   #filename.txt = name[0]
                    self.gtfs_values.append(name[2:]) #header = name[1], so data = name[2:]
     
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        with open(os.path.dirname(os.path.abspath(__file__))+'\\'+'errors.txt', 'a') as f:
            f.write(self.errors)
        #close up the connection
        try: self.conn.close()
        except RuntimeError:
            print 'ER5.ODBC'
            self.errors += 'ER5.ODBC' + '\n'
    
    #takes a gtfs file name and a table of values to insert
    #maps it to the MSSQL DB tables and attempts to make
    #a valid atomic MSSQL INSERT transaction
    def parse(self):
        for j in range(0,len(self.gtfs_names)):
            map_row = []
            sql,v = [],[]
            try:
                map_row = self.map[self.gtfs_names[j]] #get a map row if it exists
                for gtfs_row in self.gtfs_values[j]:  #each row from gtfs file
                    #swap defaults values in map from input table and store in self.V
                    for i in range(0,len(gtfs_row)):
                        #print ('value: '+gtfs_row[i]+'\n')
                        try:
                            if gtfs_row[i] != '': map_row[i+1] = gtfs_row[i]
                        except IndexError:
                            print ('template defaults: ')
                            print map_row
                            print ('gtfs row data: ')
                            print gtfs_row
                            print ('gtfs_row='+str(len(gtfs_row))+
                                   '\nmaprow='+str(len(map_row))+
                                   '\nindex i='+str(i)+'\n')
                    if self.gtfs_names[j] == 'stop_times.txt':
                        v.append(self.correct_stoptimes(map_row[1:]))
                    else:
                        v.append(map_row[1:])
                
                    #build an injection safe SQL insert from length of self.V
                    n,s = len(map_row[1:]), '('
                    if n >= 1: s += '?'
                    for i in range(1,n): s += ',?'
                    s += ')'
                    sql.append('INSERT INTO %s VALUES %s' % (map_row[0],s))
            except KeyError: print 'Key not Found, Ill formed GTFS: ER06.GTFS'
            self.SQL.append(sql)
            self.V.append(v)

    def run(self):
        self.parse()
        for j in range(0,len(self.gtfs_names)):
            print ('\nnow processing '+self.gtfs_names[j]+"\n")
            self.errors += ('\nnow processing '+self.gtfs_names[j]+"\n")
            for i in range(0,len(self.gtfs_values[j])):
                self.query(self.SQL[j][i],self.V[j][i],False)
        
    def correct_stoptimes(self,V):
        #10 columns, arrival_time is index 1, departure is index 2
        #arrival_day is index 9, departure_day is index 10
        a_time,d_time = V[1],V[2]
        a_day,d_day   = int(V[9]),int(V[10])

        #handle arrival overflow
        a_time = a_time.split(':')
        a_hr,a_min,a_sec = int(a_time[0]),a_time[1],a_time[2]
        if a_hr >= 24:
            a_day = str(a_hr/24)
            a_hr  = a_hr%24
                                 
        a_time = str(a_hr).zfill(2) + ':' + a_min + ':' + a_sec
        
        #handle departure overflow
        d_time = d_time.split(':')
        d_hr,d_min,d_sec = int(d_time[0]),d_time[1],d_time[2]
        if d_hr >= 24:
            d_day = str(d_hr/24)
            d_hr  = d_hr%24
                                 
        d_time = str(d_hr).zfill(2) + ':' + d_min + ':' + d_sec

        return [V[0],a_time,d_time,V[3],V[4],V[5],V[6],V[7],V[8],a_day,d_day]
