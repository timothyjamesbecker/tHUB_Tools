#tHUB Project UCONN: http://www.thub.uconn.edu
#LEHD MSSQL Import Tool v 2.5
#Timothy Becker, Graduate Research Assistant
#adapts LEHD data read according to tech doc Rev.20130606
#to autogenerated TSQL code and offers table creation with
#primary key constraints, table deletion and table insertion
#with injection-safe strings via ODBC connection ibtained
#from the MSSQL superclass


import os
import re
import time
import mssql
import file_tools

class LEHD2MSSQL(mssql.MSSQL):
    #constructor takes the lehd directory where the .gz files are
    #knows the file naming convention as listed in the REV 2013066 DOC
    def __init__(self,drv,srv,db,lehd_dir):
        mssql.MSSQL.__init__(self,drv,srv,db) #start up DB connection
        self.ft = file_tools.File_Tools()
        self.bind_db()
        #use this to populate all needed extra fields
        self.regex = {'level':'.csv.gz',
                      'state':'^[a-zA-Z]{2}',
                      'fork' :'od{1}|wac{1}|rac{1}',
                      'part' :'main{1}|aux{1}',
                      'seg'  :'S000{1}|SA{1}\d{2}|SE{1}\d{2}|SI{1}\d{2}',
                      'type' :'JT{1}\d{2}',
                      'year' :'\d{4}'}
        self.fields = ['state','fork','part','segment','type','year']
        #OD  has 13 fields last not needed-> row[0:11] insert type and year
        #RAC has 43 fileds last not needed-> row[0:41] insert seg, type and year
        #WAC has 53 fileds last not needed-> row[0:51] insert seg, type and year
        self.types = {'OD' :[str,str,str,str]+[int for i in range(0,10)],
                      'RAC':[str,str,str,str]+[int for i in range(0,41)],
                      'WAC':[str,str,str,str]+[int for i in range(0,51)]}
        self.pks ={'OD': lambda x: x[0:4],#gives us w_geocode,h_geocode,type,year
                   'RAC':lambda x: x[0:4],#gives us h_geocode,segment,type,year
                   'WAC':lambda x: x[0:4]}#gives us w_geocode,segment,type,year
        self.pk_suffix = '_pk'
        #work on this for table creation
        self.sqltypes = {'OD' :['char(15)'for i in range(0,4)]+['int' for i in range(0,10)],
                         'RAC':['char(15)'for i in range(0,4)]+['int' for i in range(0,41)],
                         'WAC':['char(15)'for i in range(0,4)]+['int' for i in range(0,51)]}
        self.sqltables = ['LEHD_OD','LEHD_RAC','LEHD_WAC']
        #nicely extract data that is needed while leaving the rest behind
        self.select ={'OD' :lambda x,y: x[0:2]+y[4:]+x[2:12],
                      'RAC':lambda x,y: [x[0]]+y[3:]+x[1:42],
                      'WAC':lambda x,y: [x[0]]+y[3:]+x[1:52]}
        self.header = [] #for reading one gzipped file at a time
        self.geocode = ''
        self.data = []   #into a new or already opened DB conn insert
        self.data_uniform = False
        self.meta = []
        self.table_name = ''
        self.dir = lehd_dir
        self.files = self.partition_files()
        self.curr_file = None
        
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        #with open(os.path.dirname(os.path.abspath(__file__))+'\\'+'errors.txt', 'a') as f:
        #    f.write(self.errors)
        #close up the connection
        try: self.conn.close()
        except RuntimeError:
            print 'ER5.ODBC'
            self.errors += 'ER5.ODBC' + '\n'

    #seperates files that are in a directory by state and od/wac/rac groups
    def partition_files(self):
        state = {}
        files = os.listdir(self.dir)
        files.sort() #sort so states are together, then forks, etc
        for lehd in files:
            meta = self.get_meta(lehd)
            S,F = meta[0],meta[1]
            if S+F!= '':
                if state.has_key(S):
                    if state[S].has_key(F):
                        t = state[S][F]
                        t.append(lehd)
                        state[S].update({F:t})
                    else:
                        state[S].update({F:[lehd]})
                else:
                    state.update({S:{F:[lehd]}})
        return state

    def get_meta(self,name):
        meta = []
        meta.append(re.search(self.regex['state'],name))
        meta.append(re.search(self.regex['fork'],name))
        meta.append(re.search(self.regex['part'],name))
        meta.append(re.search(self.regex['seg'],name))
        meta.append(re.search(self.regex['type'],name))
        meta.append(re.search(self.regex['year'],name))
        for i in range(0,len(meta)):
            if meta[i]!=None: meta[i] = meta[i].group(0).upper()
            else: meta[i] = ''
        return meta

    #given the meta-data patterns for ST-OD|WAC|RAC
    #parse and form a canonical table name
    def get_table_name(self,meta):
        geo = {2:'S',5:'C',11:'T',12:'G',15:'B'}
        return 'LEHD_'+meta[1]+'_'+geo[len(self.geocode)] #LEHD_OD, LEHD_WAC, LEHD_RAC
    
    #read one file at a time, cleaning, processing and annotating
    #saving into self.header and self.data when all is correct
    def read(self,next_file):
        self.data = []
        self.meta = self.get_meta(next_file)
        temp = self.ft.read_gzip_csv(self.dir+next_file,[])
        self.header = self.select[self.meta[1]](temp[1],self.fields)
        print('Header contains: '+str(len(self.header))+' fields')
        print(self.header)
        if len(temp)>2:
            self.geocode = temp[2][0]
            print('GeoCode is %s'%self.geocode)
            sniff = self.select[self.meta[1]](temp[2],self.meta)
            print('Sniffer First Payload: '+','.join(sniff))
            for row in temp[2:]:
                x = self.select[self.meta[1]](row,self.meta)
                if(len(x) > 55):print('Row has '+str(len(x))+' values')
                for i in range(0,len(x)):
                    try: #most regular int will parse fine without raising exceptions
                        x[i] = self.types[self.meta[1]][i](x[i]) #might not have to do this
                    except ValueError: #large values have been discovered to be in SCI notation
                        try: x[i] = self.types[self.meta[1]][i](float(x[i])) #try unpacking SCI notation
                        except ValueError:
                            print('Value of ' + x[i] + 'not valid!') #no hope now
                            #should add some error report here using the built in error system
                            self.errors += 'ER6.FileParsingInValid'+'\n'
                self.data.append(x)
            self.table_name = self.get_table_name(self.meta) #set SQL table name
            self.curr_file = next_file                       #set file pointer
            self.data_uniform = all([len(i)==len(self.data[0]) for i in self.data]) #row length uniformity
            return True    #had some data to process
        else: return False #nothing to proccess data is empty
        
    #attach to default DB for all operations
    def bind_db(self):
        try:
            self.SQL = 'USE %s' % self.db
            self.V = []
            self.query(self.SQL,self.V,False)
        except Exception:
            er = 'ER9:DB Name Error: '+self.db+' Not Valid'
            print(er)
            self.errors += er + '\n'

    #check for existance of a specific table in the DB
    #this one doesn't need exception handling because it is a check        
    def table_exists(self,s=''): 
        if s == '': s = self.table_name
        self.SQL = """IF OBJECT_ID ('%s', 'U') IS NOT NULL
                    BEGIN SELECT 1 END ELSE BEGIN SELECT 0 END""" % s
        self.V = []
        response = self.query(self.SQL,self.V,True)
        if response[0][0] == 1: return True
        else: return False
        
    #table deletion if needed, added as a convience feature
    #this one doesn't need exception handling because it has a check
    def table_delete(self,s=''):
        if s == '': s = self.table_name
        #first delete _pk constraints for a DB that has them
        self.SQL =  """  
        DECLARE @database nvarchar(50)
        DECLARE @table nvarchar(50)
        SET @database = '%s'
        SET @table = '%s'
        DECLARE @sql nvarchar(255)
        WHILE EXISTS(
                        SELECT *
                        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
                        WHERE constraint_catalog = @database AND table_name = @table
                    )
        BEGIN
            SELECT  @sql = 'ALTER TABLE ' + @table + ' DROP CONSTRAINT ' + @table + '%s' 
            FROM    INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
            WHERE   constraint_catalog = @database AND 
                table_name = @table
            EXEC    sp_executesql @sql
        END""" % (self.db,s,self.pk_suffix)
        self.V = []
        self.query(self.SQL,self.V,False)
        #now drop the table if it is there next
        self.SQL = """IF OBJECT_ID ('%s', 'U') IS NOT NULL DROP TABLE %s""" % (s,s)
        self.V = []
        self.query(self.SQL,self.V,False)

    #programmatically generate a new LEHD table    
    def table_create(self):
        #check if the table is there
        print('Table Exists? '+str(self.table_exists()))
        #use the type-specific mapping to form the primary key line at the end
        if not self.table_exists():
            n,m,s = len(self.header),len(self.sqltypes[self.meta[1]]),'('
            if n == m:
                if n >= 1: s+= '['+self.header[0]+'] '+self.sqltypes[self.meta[1]][0]
                for i in range(1,n): s+= ', ['+self.header[i]+'] '+self.sqltypes[self.meta[1]][i]
                #pk line must go here with a constraint that matches the one in table_delete
                pks = ','.join(self.pks[self.meta[1]](self.header))
                s+=', CONSTRAINT %s%s primary key (%s)' %(self.table_name,self.pk_suffix,pks)
                s+= ')'
                self.SQL = """CREATE TABLE %s %s
                           """ %(self.table_name,s)
                self.V = []
                self.query(self.SQL,self.V,False)
            else:
                er = 'ER7: Create Table: '+ self.table_name +' :Data Format Header Malformed!'
                print(er)
                self.errors += er + '\n'

    #once you have a valid table name, deposit all data payload
    def table_insert(self):
        self.SQL,self.V = [],[]
        #build one insert SQL form to use on each row of conforming data
        try:
            n,s = len(self.header),'('
            if n >= 1: s += '?'
            for i in range(1,n): s += ',?'
            s += ')'
            self.V = self.data
            self.SQL = 'INSERT INTO %s VALUES %s' % (self.table_name,s)
        except Exception:
            er = 'ER8: Insert Table: '+ self.table_name +' :Issues!'
            print(er)
            self.errors += er + '\n'
        k = 0
        print(' (.) means a 1000 successes:')
        #row by row injection safe table insertion over an odbc conn
        for v in self.V:
            try:
                self.query(self.SQL,v,False)
                if k%1000==0: print '.',
                k = (k+1)%1000
            except Exception:
                er = 'ER8: Insert Table: '+ self.table_name +' :Issues: '+v
                print(er)
                self.errors += er + '\n'

    #read in gzipped compressed lehd files, partition, filter, process and
    #automatically formulate TSQL table createion, and by row insertion
    #with fully sheilded error handling
    def process_batch(self,perge=False):
        #optional perge or reset all in begining
        if perge:#flag to delete all LEHD tables
            for i in self.sqltables:
                print('Perging Table: '+i)
                self.table_delete(i)
        #pullout the self.file map which has partitions of LEHD files to process    
        for ST in self.files: #by state
            for TY in self.files[ST]:     #by type
                for F in self.files[ST][TY]:
                    start = time.clock()
                    print("Processing File: "+F)
                    print("Reading .gz Compression into Dataframe")
                    if(self.read(F)): #read the data
                        print("Creating Table")
                        self.table_create() #create the table if needed
                        print 'Starting Insertion Commands',
                        self.table_insert() #injection safe insertion
                        elapsed = (time.time()-start) #this is in seconds
                        minutes = int(elapsed/60)
                        seconds = elapsed/60 - minutes
                        print('Minutes to Process '+F+' :'+str(minutes)+':'+str(seconds))
                    else: print("No Data at: "+F)

            

    

    
