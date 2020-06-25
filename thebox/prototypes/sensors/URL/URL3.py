

from urllib.parse import urlparse
import os
import operator
import sqlite3
from collections import OrderedDict
import matplotlib.pyplot as pyplot
import pandas as pd
from pandasql import sqldf
import json
import datetime
import subprocess
import re

network_Information = str(subprocess.check_output(["netsh","wlan","show","network"]))
osAuthEnt=re.search('Authentication.*WPA2-Enterprise', network_Information) 
osAuthPer=re.search('Authentication.*WPA2-Personal', network_Information) 
pysqldf = lambda q: sqldf(q, globals())

if os.path.isfile('C:/main/URLResult4.csv'):
    print("yes")
    resultdf=pd.read_csv(r'C:/main/URLResult2.csv')
    dfTimeStamp=resultdf['timeStamp'].max()
else:
    print("no")
    colNames=['id','timeStamp','date','URL','title','label']
    resultdf=pd.DataFrame(columns=colNames)
    dfTimeStamp=0
    
#resultdf=pd.read_csv(r'C:/main/AppResult.csv')
# chrome History

data_path=os.path.expanduser('~')  + "\\AppData\\Local\\Google\\Chrome\\User Data\\Default"

history_db=os.path.join(data_path,'history')
c=sqlite3.connect(history_db)
cursor=c.cursor()
select_statement="SELECT * FROM urls;"

cursor.execute(select_statement)
results=(cursor.fetchall())
a=results[5]>(1601,1,1)
print(results)
i=0
for record in results:
    i=i+1
  
    visit_time = str(datetime.datetime(1601,1,1) + datetime.timedelta(microseconds=record[5]))
    if visit_time[:4] == "1601":
        pass
    else:
        visit_time = str(datetime.datetime.strptime(visit_time, "%Y-%m-%d %H:%M:%S.%f"))
        visit_time = visit_time[:-7]
    if (i<=103):
        resultdf.loc[len(resultdf)]=[i,record[5],visit_time,record[1],record[2],"work"] 
    else:
         resultdf.loc[len(resultdf)]=[i,record[5],visit_time,record[1],record[2],"play"] 
print(resultdf)
resultdf.to_csv (r'C:/main/URLResult2.csv',header=True)