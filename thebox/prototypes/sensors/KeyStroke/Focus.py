
import win32gui 
import time
#from win32gui import GetWindowText, GetForegroundWindow

#print (GetWindowText(GetForegroundWindow()))
#while True:
    #print(win32gui.GetWindowText(win32gui.GetForegroundWindow()))
    #time.sleep(0.5)
import Tkinter
p = Tkinter.Tk()
print(p.winfo_pointerxy())