import re
import csv

path = 'C:\\Users\\tbecker\\Documents\\tHUB\\DATA_FIPS\\'
name = 'census_states.txt'
new_name = 'states.txt'
text = []

with open(path+name, 'rb') as f:
    for line in f:
        text.append(line)

print(len(text))

for i in range(0,len(text)):
    text[i] = text[i].replace('<option value="','')
    text[i] = text[i].replace('">',',')
    text[i] = text[i].replace('</option>','')
    text[i] = text[i].replace('\r\n','')
    
print(len(text))

with open(path+new_name, 'wb') as f:
    writer = csv.writer(f)
    for t in text: writer.writerow([t])
