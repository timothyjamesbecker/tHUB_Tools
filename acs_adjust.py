import os
import re
import sys
import file_tools
ft = file_tools.File_Tools()

#process block groups
base = '..\\DATA_ACS\\'
folders = [base+'acs5yr_blockgroup_2010\\',base+'acs5yr_tract_2010\\',
           base+'acs5yr_blockgroup_2011\\',base+'acs5yr_tract_2011\\']
files = ['B01001.csv','B01001H.csv','B01001I.csv','B01002.csv',
         'B02001.csv','B06007.csv','B06010.csv','B06011.csv','B06012.csv',
         'B11004.csv','C18101.csv','B18102.csv','B18103.csv','B18105.csv']

for folder in folders:
    m_b = re.search('block',folder)
    m_t = re.search('tract',folder)
    print('Processing folder: '+ folder)
    new_folder = base+folder[12:len(folder)-1]+'_adjusted\\'
    print(new_folder)
    if not os.path.exists(new_folder): os.makedirs(new_folder)
    for f in files:
        if f not in os.listdir(folder):
            print('Missing Files for : ' + folder + f)
        else:
            print('\nProcessing Files for : ' + folder + f)
            text = ft.read_csv(folder+f,[],'"','NULL')
            header = text[1][0:1]+text[1][8:]+['ACS5_END_YEAR']
            print(header)

            data = []
            types = [str]+[int for j in range(1,len(header)-1)]+[str]
            if(m_b is not None and f == 'B01002.csv'):
                types = ([str]+[int for l in range(0,3)]+
                         [float for j in range(3,len(header)-1)]+[str])
            if(m_t is not None and f == 'B01002.csv'):
                types = ([str]+[int for l in range(0,2)]+
                         [float for j in range(3,len(header)-1)]+[str])
            for j in text[1:]: #this is each row in the data
                row = j[0:1]+j[8:]+[folder[-5:-1]]
                data.append(row) #get rid of garbage acs
            
            for i in range(0,len(data)): #convert the types
                for j in range(0,len(data[i])):
                    data[i][j] = data[i][j].replace("'",'')
                    try: data[i][j] = types[j](data[i][j])
                    except ValueError: data[i][j] = ''
                    
            print(data[1:3])
            new_file = new_folder+f
            ft.write_csv(new_file,header,data[1:],[])
            
            
        
        
        



