

from urllib.parse import urlparse
import os
import operator
import sqlite3
from collections import OrderedDict
import matplotlib.pyplot as pyplot
import pandas as pd
from pandasql import sqldf
import json

pysqldf = lambda q: sqldf(q, globals())

# chrome History
data_path=os.path.expanduser('~')  + "\\AppData\\Local\\Google\\Chrome\\User Data\\Default"

history_db=os.path.join(data_path,'history')
c=sqlite3.connect(history_db)
cursor=c.cursor()
select_statement="SELECT urls.url,urls.visit_count FROM urls, visits WHERE urls.id=visits.url;"

cursor.execute(select_statement)
results=cursor.fetchall()
sites_count={}
i=0
colNames=['id','URL','Label']
resultdf=pd.DataFrame(columns=colNames)
    
for url,count in results:
    i=i+1
    result = urlparse(url)
    if (i<=103):
        resultdf.loc[len(resultdf)]=[i,url,"work"] 
    else:
         resultdf.loc[len(resultdf)]=[i,url,"play"] 
print(resultdf)
resultdf.to_csv (r'C:/main/URLResult.csv',header=True)