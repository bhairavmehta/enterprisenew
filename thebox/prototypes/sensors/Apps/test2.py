import subprocess
cmd = 'WMIC PROCESS get Caption,Commandline,Processid'
proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
print(proc.stdout)
for line in proc.stdout:
    print (line)
    break
   
