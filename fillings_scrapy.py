# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 14:51:15 2019

@author: Hengxu Lin
"""

import requests
import os
import pandas as pd
import re
 
#from bs4 import BeautifulSoup as bs



#f = fr.freader('F:\\11to\\annual_report\\119726-SANDISK CORP-2011-2-23.txt')

df= pd.read_csv('edgar_idx.csv',index_col = 0)
'''
1994:1916
1995:4134
1996:8450
1997:15147
1998:22077
1999:28838
2000:35490
2001:41738
2002:48497
2003:56965
2004:65532
2005:74549
2006:83401
2007:91975
2008:100721
2009:110560
2010:119725
2011:128566
2012:136958
2013:145063
2014:153147
'''

patt = re.compile(r'<FILENAME>(.*?)(?=<FILENAME>)',flags=re.I|re.S)
for row in range(128562,128566):#range(129100,136959)
    try:
        conm = str(df.loc[row,'conm'])
        saveas = str(row)+'-'+conm+'-'+str(df.loc[row,'date'].replace('/','-'))
        url = 'https://www.sec.gov/Archives/' + str(df.loc[row,'path']).strip()
    
        if not os.path.exists('annual_report'):
                os.makedirs('annual_report')
            
        text = requests.get('%s'%url).content.decode(encoding = 'utf-8')
        text = re.search(patt,text)[0]
        with open('annual_report\%s.txt'%saveas, 'w') as f:
            f.write(text)
            print (saveas, 'downloaded and wrote to text file' )
    except:pass
#    cf = fr.freader('F:\\11to\\annual_report\\'+saveas+'.txt',file_type='htm')
#    cf.to_csv()
#    print(saveas, 'downloaded and wrote to csv file')
        
    
print ('All test done.')



