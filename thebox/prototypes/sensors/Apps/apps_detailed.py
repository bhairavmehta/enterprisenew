import os
import psutil
import time
 
logPath = r'C:\temp'
if not os.path.exists(logPath):
    os.mkdir(logPath)
 
separator = "-" * 80
format = "%7s %7s %12s %12s %30s, %s"
format2 = "%7.4f %7.2f %12s %12s %30s, %s"
while 1:
    procs = list(psutil.process_iter()) #get_process_list()
    #procs = sorted(procs, key=lambda proc: proc.name)
 
    logPath = r'C:\temp\procLog%i.log' % int(time.time())
    f = open(logPath, 'w')
    f.write(separator + "\n")
    f.write(time.ctime() + "\n")
    f.write(format % ("%CPU", "%MEM", "VMS", "RSS", "NAME", "PATH"))
    f.write("\n")
 
    for proc in procs:
        cpu_percent = proc.get_cpu_percent()
        mem_percent = proc.get_memory_percent()
        rss, vms = proc.get_memory_info()
        rss = str(rss)
        vms = str(vms)
        name = proc.name
        path = proc.path
        f.write(format2 % (cpu_percent, mem_percent, vms, rss, name, path))
        f.write("\n\n")
    f.close()
    print ("Finished log update!")
    time.sleep(300)
    print ("writing new log data!")