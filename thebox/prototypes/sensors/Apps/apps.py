import win32com.client
import datetime
import pandas as pd
import subprocess
import re

network_Information = str(subprocess.check_output(["netsh","wlan","show","network"]))
osAuthEnt=re.search('Authentication.*WPA2-Enterprise', network_Information) 
osAuthPer=re.search('Authentication.*WPA2-Personal', network_Information) 

colNames=['DateTime','Process','Label']

resultdf=pd.read_csv(r'C:/main/AppResult.csv')
wmi=win32com.client.GetObject('winmgmts:')
for p in wmi.InstancesOf('win32_process'):
    osAuthEnt=re.search('Authentication.*WPA2-Enterprise', network_Information) 
    osAuthPer=re.search('Authentication.*WPA2-Personal', network_Information) 
    if (osAuthEnt):
        resultdf.loc[len(resultdf)]=[datetime.datetime.now(),p.Name,"work"]  
    else: 
        resultdf.loc[len(resultdf)]=[datetime.datetime.now(),p.Name,"play"]  
resultdf.to_csv (r'C:/main/AppResult.csv',index=False,header=True)


