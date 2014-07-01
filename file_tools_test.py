#File Tools Test v 0.2, 09/23/2013-09/30/2013
#Timothy Becker, UCONN/SOE/CSE/Graduate Research Assistant
#Test Script for reading & writing to both
#uncompressed .csv files, and compressed .zip and .gz .csv files

import os
import file_tools #class
ft = file_tools.File_Tools()
test_folder = '.\\test_files\\'
file_names = os.listdir(test_folder)

for f in file_names:
    print('Testing File: ' + f)
    #test .csv read alone
    if(f.endswith('.txt') or f.endswith('.csv')):
        f = test_folder + f
        #shows example of applying field type conversion
        field_types = [str,str,int,int,int,int,int,int,int,int,int,int,str]
        text = ft.read_csv(f,field_types)
        print(str(len(text)) + ' lines read from ' + f +
              ' using CSV reader')
        print('top ten rows:')
        for i in text[0:10]: print(i)
        #write test here
        new_f = f.replace('.txt','').replace('.csv','') + '_write.csv'
        ft.write_csv(new_f,text,[])
        
    #test .zip read into .csv
    if(f.endswith('.zip')):
        f = test_folder + f
        #when field type list is empty, str type is used
        text = ft.read_zip_csv(f,[])
        print(str(len(text)) + ' lines read from ' + f +
             ' using ZIP Decoder and CSV reader')
        print('top ten rows:')
        for i in text[0:10]: print(i[1:10])
        #write test here
        new_f = f.replace('.zip','') + '_zipwrite.zip'
        ft.write_csv_zip(new_f,text,[])

    #test .gzip read into .csv
    if(f.endswith('.gz')):
        f = test_folder + f
        #when field type list is empty, str type is used
        text = ft.read_gzip_csv(f,[])
        print(str(len(text)) + ' lines read from ' + f +
             ' using GZIP Decoder and CSV reader')
        print('top ten rows:')
        for i in text[0:10]: print(i)
        #write test here
        new_f = f.replace('.gz','') + '_gzipwrite.gz'
        ft.write_csv_gzip(new_f,text,[])
