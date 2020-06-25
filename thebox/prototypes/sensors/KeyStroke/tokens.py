import pandas as pd
import numpy as np
from collections import defaultdict

def replaceMultipleChar(st,charsList,newSt):
    for oldChar in charsList:
            st=st.replace(oldChar,newSt)
    return st

fiename='c:\\temp\\trainingSamples\\S2.txt'
df=pd.DataFrame(columns=['focus', 'token'])
#f= open('c:\\temp\\Priscila\\test-0910.txt','r',encoding="utf8",newline='')  
f= open(fiename,'r',encoding="utf8",newline='')  
st=f.read()
#print(st)
st=replaceMultipleChar(st,['Key.caps_lock'],'')
st=replaceMultipleChar(st,['Key.space'],' ')
k=st.split(':::')
print(k[0])
print(k[1])
i=1
delSt=""
words=""
while i<len(k):
    sub=k[i].split(':?')
    sub[0]=sub[0].replace('Focus:-:','')
    sub[0]=sub[0].replace(':?','')
    print (sub[0])
    print(sub)
    
    if sub[1]!='':
        print(sub[1])
    while sub[1].find('Key.backspace')>0:
        keyindex=sub[1].find('Key.backspace')
        #print(sub[1][keyindex-1:keyindex])
        delSt=delSt+sub[1][keyindex-1:keyindex]
        if keyindex>0:
            #print(sub[1][0:keyindex-1]+sub[1][keyindex+13:None])
            sub[1]=sub[1][0:keyindex-1]+sub[1][keyindex+13:None]
    sub[1]=replaceMultipleChar(sub[1],['Key.enter','.',',',':','?'],' ')
    df.loc[i]=sub
    list1=sub[1].split()
    words=[*words , *list1]
    
    i=i+1 
f.close() 
print(df)
print(delSt)
print (words)
chars = defaultdict(int)
charsIndex=list(set(delSt))
print(charsIndex)
for char in charsIndex:
    chars[char]=delSt.count(char)
    print(chars[char]," ",char)

wordSt = defaultdict(int)   
wordIndex=list(set(words))
for word in wordIndex:
    wordSt[word]=words.count(word)
    print(wordSt[word]," ",word)
#print(wordIndex)
print(delSt)
