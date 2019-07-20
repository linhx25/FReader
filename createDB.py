##http://kaikaichen.com/?p=59
# Generate the list of index files archived in EDGAR since start_year (earliest: 1993) until the most recent quarter
import datetime
import sqlite3
import requests
import pandas as pd
from sqlalchemy import create_engine
import csv
import os,re

current_year = datetime.date.today().year
current_quarter = (datetime.date.today().month - 1) // 3 + 1
start_year = 1993
next_year=2018
#years = list(range(start_year, current_year))
years = list(range(start_year, next_year)) #[)
quarters = ['QTR1', 'QTR2', 'QTR3', 'QTR4']
history = [(y, q) for y in years for q in quarters]
#for i in range(1, current_quarter + 1):   #这里要改小点，要不有memeory error
    #history.append((current_year, 'QTR%d' % i))
urls = ['https://www.sec.gov/Archives/edgar/full-index/%d/%s/master.idx' % (x[0], x[1]) for x in history]  #%d表示十进制证书，#表示字符串
urls.sort()  #下载master.idx的地方，里面的内容


# Download index files and write content into SQLite

con = sqlite3.connect('edgar_idx.db')   #链接或创建数据库
cur = con.cursor()             #创建一个游标, 以元组的形式展示
cur.execute('DROP TABLE IF EXISTS idx')  #如果数据表已经存在，则使用execute()方法删除
cur.execute('CREATE TABLE idx (cik TEXT, conm TEXT, type TEXT, date TEXT, path TEXT)')

for url in urls:
    lines = requests.get(url).text.splitlines()    #这一季idx文本的逐行读取,四个季度整合在一起
    records = [tuple(line.split('|')) for line in lines[11:]]
    cur.executemany('INSERT INTO idx VALUES (?, ?, ?, ?, ?)', records)
    print(url, 'downloaded and wrote to SQLite')

con.commit()    
con.close()     


# Write SQLite database to Stata
engine = create_engine('sqlite:///edgar_idx.db')     #(r’sqlite:///C:\path\to\edgar_idx.db’)
#sqlite:/// 指明了数据库的类型
with engine.connect() as conn, conn.begin():
    data = pd.read_sql_table('idx', conn)
    data = data[data.type=='10-K']
    data.index = range(1,len(data)+1)
    #data['conm'] = data['conm'].str.replace('\s\s+',' ')
    #data.to_stata('edgar_idx2010.dta')
    data.to_csv('edgar_idx.csv')

with open('edgar_idx.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for line in reader:
        conm = re.sub('[\\\\/]','',line[2]) 
        saveas = line[0] + '-' + conm + '-' + line[4].replace('/', '-') #公司名+日期
        #saveas = '-'.join([line[0], line[1].replace('/', '-'), line[2].replace('/', '-'), line[3]])
        # Reorganize to rename the output filename.
        url = 'https://www.sec.gov/Archives/' + line[5].strip()
        print(saveas)
        #with open(saveas, 'wb') as f:
        if not os.path.exists('annual_report'):
            os.makedirs('annual_report')
        with open('annual_report\%s.txt'%saveas, 'wb') as f:
            f.write(requests.get('%s'%url).content)
            print(url, 'downloaded and wrote to text file')
###stata
#clear
#insheet using "C:\Users\yushi\PycharmProjects\SECEdgar\edgar_idx2011.csv"
#keep if type=="10-K"
#outsheet using "C:\Users\yushi\PycharmProjects\SECEdgar\sample2011.csv", comma replace