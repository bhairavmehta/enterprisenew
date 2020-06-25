import wmi
import django
from django.conf import settings
from django.apps import apps

# get complete list of all apps
#list_of_apps = [apps.get_app_config(app_name.split('.')[-1]) for app_name in settings.INSTALLED_APPS]
#for app_name in settings.INSTALLED_APPS:
    #print(app_name)
c = wmi.WMI ()
print(c.Win32_Process.methods.keys())
print(c.Win32_Process.properties.keys())
print(c.Win32_Service.properties.keys())
#for process in c.Win32_Process ():
  #print (process.ProcessId,process.CreationDate,process.CSName,"  * ",process.TerminationDate,"   ",process.PageFaults,process.SessionId,process.ExecutionState,process.Name,process.CommandLine," ****EPath=",process.ExecutablePath,process.InstallDate)


for s in c.Win32_Service():
 # filter service names
    
    print(s.State, s.StartMode, s.Name, s.DisplayName,s.ProcessId,s.Caption,"  *   ",s.ServiceType,"  *   ",s.InstallDate,s.PathName)