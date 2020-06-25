import os
import psutil
import time

listOfProcessNames = list() 
print(psutil.cpu_times())
print(psutil.sensors_battery())
print(psutil.users())
procs = list(psutil.process_iter()) #get_process_list()
    #procs = sorted(procs, key=lambda proc: proc.name)
 
   
for proc in procs:
   # p = psutil.Process(os.getpid())
    p = psutil.Process(proc.pid)

    #print(p.cpu_percent())
    #print(p.memory_info())
    #print(proc)
    pInfoDict = proc.as_dict(attrs=['pid', 'name', 'cpu_percent','username','open_files'])
    pInfoDict['vms'] = proc.memory_info().vms / (1024 * 1024)
   # Append dict of process detail in list
    listOfProcessNames.append(pInfoDict)

print (listOfProcessNames)



