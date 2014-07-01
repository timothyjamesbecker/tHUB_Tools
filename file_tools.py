#File Tools v 0.6, 09/23/2013-09/30/2013
#Timothy Becker, UCONN/SOE/CSE/Graduate Research Assistant
#Set of file format tools that wrap up several libraries
#and provide simple methods for reading & writing to both
#uncompressed .csv files, and compressed .zip and .gz .csv files
#using memory streams and no OS calls or additional file writes
#facilitating efficient and powerful compressed File IO

import csv
import gzip
import zipfile
import re
import itertools
from io import BytesIO
from cStringIO import StringIO

class File_Tools:
    #assumes a standard list-of-list table structure built as follows:
    #(all values are strings for easy parsing/writing and conversion)
    #table[0]  -> 'filename.suffix'
    #table[1]  -> header(column/field names)
    #table[1:] -> data (rows/instances)

    #constructor for future use
    #def __init__(self, in_dir='.\\', out_dir='.\\'):
    #    self.in_dir  = in_dir
    #    self.out_dir = out_dir

    #def __enter__(self):

    #destructor for future use
    #def __exit__(self):

    #given a CSV encoded filename, reads the .csv and
    #returns a table of type converted data using types list
    #passing a type list is all or nothing for now (error reporting later)
    #note this basic reader has the most sophisticated dialect sniffer that
    #the other compression-readers should impliment in the future...
    def read_csv(self,filename,types=[],quote='"',default='null'):
        table = [filename]
        with open(filename, 'rb') as csvfile:
            try:#-----------------------------------------------
                dialect = csv.Sniffer().sniff(csvfile.read(1024))
            except csv.Error:
                print('Malformed CSV Dialect forcing into excel mode...')
                dialect = 'excel'
            #---------------------------------------------------
            csvfile.seek(0)         #rewind to the begining
            reader = csv.reader(csvfile, dialect,quotechar=quote)
            header = next(reader)   #sniff out the header
            col_n  = len(header)    #number of columns
            if types==[]:types = [str for i in range(0,col_n)]
            table.append(header)    #always keep the header as strings
            j,last = 1, [0,0]
            for row in reader:      #read and apply type conversions
                j = j + 1
                try:#-------------------------------------------------------
                    #insert default values for any that are missing
                    new_row = row
                    for r in range(0,len(new_row)):
                        if new_row[r] == '' or new_row is None: new_row[r] = default
                    new_row = [types[i](new_row[i]) for i in range(0,len(new_row))]
                    table.append(new_row+[types[i](default) for i in range(len(new_row),col_n)])
                except IndexError:
                    if(last != [col_n,len(row)]):
                        last = [col_n,len(row)]
                        print('>>>------->>>Error Parsing Line: '+str(j))
                        print('--->>>>>>>---# of values expected: '+str(col_n))
                        print('>>>------->>># of values read:     '+str(len(row)))
                        print(header)
                        print(new_row)
                #-----------------------------------------------------------
        return table
    
    #given a ZIP compressed CSV encoded filename, uncompresses the .zip
    #saving to a temp stream curr_zipfiles before reading the .csv files and
    #returning a table of type converted data using types list
    #for now we assume that the heirchy is flat (no nested folder, etc)
    #passing a type list is all or nothing for now (error reporting later
    def read_zip_csv(self,filename,types):
        tables = [filename]
        with zipfile.ZipFile(filename, 'r') as root:
            print(root.namelist())
            for name in root.namelist():
                try:
                    table = [name]
                    stream = StringIO(root.read(name))
                    reader = csv.reader(stream, dialect=csv.excel)
                    #for row in reader: table.append(row)
                    header = next(reader)   #sniff out the header
                    col_n  = len(header)    #number of columns
                    if types==[]:types = [str for i in range(0,col_n)]
                    table.append(header)    #always keep the header as strings
                    for row in reader:      #read and apply type conversions
                        table.append(row)
                    tables.append(table)
                except Exception: print("zip error")
        return tables
    
    #given a GZIP compressed CSV encoded filename, uncompresses the .gz
    #saving to a temp stream gzipfile before reading the .csv file and
    #returning a table of type converted data using types list
    #passing a type list is all or nothing for now (error reporting later)
    def read_gzip_csv(self,filename,types=[]):
        table = [filename]
        with gzip.open(filename, 'rb') as gzipfile:
            reader = csv.reader(gzipfile, dialect=csv.excel)
            header = next(reader)
            m = len(header)
            table.append(header)
            if types==[]:
                for row in reader: table.append(row)
            else:
                for row in reader:
                    try:
                        table.append([types[i](row[i]) for i in range(0,m)])
                    except ValueError:
                        print("FT01: Value Read Error at:")
                        print(row)
        return table

    #given a destination .csv filename writes a CSV encoded string
    #from the table of type converted data using types list
    #passing a type list is all of nothing for now (error reporting later)
    def write_csv(self,filename,header,table,types):
        with open(filename, 'wb') as csvfile:
            writer = csv.writer(csvfile,)
            writer.writerow(header)
            for row in table: writer.writerow(row)
        return

    #given a root directory name, and a set of tables, encodes each table
    #as a CSV file byte stream and inserts into the ZIP compressed directory
    def write_csv_zip(self,filename,tables,types):
        with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as root:
            for t in tables[1:]:  #tables[0] has .zip file name
                stream = BytesIO()
                writer = csv.writer(stream)
                for row in t[1:]: writer.writerow(row) #t[0] is the .csv filename
                root.writestr(t[0],stream.getvalue()) 
        return

    #given a root directory name, and a table, encodes as a
    #CSV file byte stream and inserts into the GZIP compressed directory
    def write_csv_gzip(self,filename,table,types):
        with gzip.open(filename, 'wb') as gzipfile:
            stream = BytesIO()
            writer = csv.writer(stream,quoting=csv.QUOTE_NONE)
            for row in table[1:]: writer.writerow(row) #table[0] is the .csv filename
            gzipfile.write(stream.getvalue())
        return

            
        
