from pynput import keyboard
import pandas as pd
import win32gui 
import tkinter
import getopt
import sys


import numpy as np
from collections import defaultdict
from sklearn import model_selection, preprocessing, linear_model, naive_bayes, metrics, svm
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn import decomposition, ensemble

import pickle
from thebox.pubsub_kafka.pubsubkafka import PubSubManagerKafka, PubSubProducer, PubSubConnectionKafka
from thebox.common.abstractmessage import AbstractMessage
from thebox.messages.inferencemessage import InferenceMessage, InferenceDataFeature


class TelemetryClient():

    def __init__(self, pubsub_endpoint: str, topic: str):
        self.kafka_mgr = PubSubManagerKafka(PubSubConnectionKafka(pubsub_endpoint))
        self.producer = self.kafka_mgr.create_producer(topic, "testapp_sig_gen")

    def SVM_features(self,s):

        valid_x=set([])
        valid_x.add(s)
        ##fi=open( 'c:\\temp\\tfidfvocabulary.pkl','rb')
        fi=open( 'tfidfvocabulary.pkl','rb')

        tfidf_vect=pickle.load(fi)


        xvalid_tfidf1 =  tfidf_vect.transform(valid_x)
        xvalid_tfidf = xvalid_tfidf1.toarray()
        
        #filename = 'c:\\temp\\svm_model.sav'
        #loaded_model = pickle.load(open(filename, 'rb'))
        #predictions=loaded_model.predict(xvalid_tfidf)
        #print("predictions",predictions )
        return xvalid_tfidf.astype(np.float32) #xvalid_tfidf
        
    def send_telemetry(self, text: str):
        
        keyStrokeFeature = np.squeeze(self.SVM_features(text))
        #print(f"{keyStrokeFeature.shape}")
        msg = InferenceMessage(
            AbstractMessage.create_new_correlation_id(),
            data_descriptor_name="demo app message",
            feature_data=[
                InferenceDataFeature("float_input", keyStrokeFeature)
            ])

        self.producer.publish(msg)
        #print(f"Message sent! {msg}")


def replaceMultipleChar(st,charsList,newSt):
        for oldChar in charsList:
                st=st.replace(oldChar,newSt)
        return st


def generateOriginalText(filename):
        
        #fiename='c:\\temp\\trainingSamples\\S2.txt'
        df=pd.DataFrame(columns=['focus', 'token'])

        f= open(filename,'r',encoding="utf8",newline='')  
        st=f.read()

        st=replaceMultipleChar(st,['Key.caps_lock','Key.shift','Key.right','Key.left','Key.esc'],'')
        st=replaceMultipleChar(st,['Key.space'],' ')
        k=st.split(':::')
        
        i=1
        delSt=""
        words=""
        doc=""
        while i<len(k):
            sub=k[i].split(':?')
            sub[0]=sub[0].replace('Focus:-:','')
            sub[0]=sub[0].replace(':?','')
        
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
            doc+=sub[1]
            words=[*words , *list1]
            
            i=i+1 
        f.close() 
    
        chars = defaultdict(int)
        charsIndex=list(set(delSt))
    
        for char in charsIndex:
            chars[char]=delSt.count(char)
        

        wordSt = defaultdict(int)   
        wordIndex=list(set(words))
        for word in wordIndex:
            wordSt[word]=words.count(word)
        return doc



def logKeyStrokes(filename):
        f= open(filename,'w',encoding="utf8",newline='')  
    
        current = pd.DataFrame(columns=['id', 'st'])
        #focus=win32gui.GetWindowText(win32gui.GetForegroundWindow())
        focus="test"
        f.write(':::Focus:-:'+focus+':?:') 
        f.close() 

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

                f.write(format(key.char)) 
                f.close()
            except AttributeError:
                f= open(filename,'a') 
            
                if key==keyboard.Key.space:
                
                    f.write(" ")
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
    
    

 

def printhelp():
    help = """
Usage:
    python signal_gen.py -i <path_to_input_image> -s <server_host:server_port> -t <ingestion_topic>
"""
    print(help)


def main():

    # Before starting this app:
    #  1. create a file server hosting the model:
    #     docker run -dit --restart always --name workplay_onnx_server -p 8082:80 -v "/home/jerry/thebox_onnx_files":/usr/local/apache2/htdocs/ httpd:2.4 
    #  2. drop the workplay onnx model there
    #  3. start/find a instance of thebox, and put in following scenario:
    #     tip: to get a swagger server: 
    #     docker run -d -p 1080:8080 --name swagger --restart always swaggerapi/swagger-ui:v2.2.9
    #     <see sceanrio.json>
    #  4. Launch notif_app.py first to listen to messages
    #  5. Run this program and type in a URL to try out

    pubsub_endpoint = "localhost:10001"
    topic = "in_topic_ks_infer_test"
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:t:", ["server=", "topic="])
    except getopt.GetoptError:
        printhelp()
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            printhelp()
            sys.exit()
        elif opt in ("-s", "--server"): # e.g. localhost:9092
            pubsub_endpoint = arg
        elif opt in ("-t", "--topic"):
            topic = arg

    telClient = TelemetryClient(pubsub_endpoint, topic)
    
    print("Connected to TheBox at endpoint: {}:{}".format(pubsub_endpoint, topic))
    print("Now imagine the date and time is somehow being provided (type 'exit' to quit)...\n")
    print("===================================================\n")
    
    #filename='c:\\temp\\trainingSamples\\ks1.txt'
    while True:    # infinite loop
        filename='c:\\temp\\trainingSamples\\ks1.txt'
        logKeyStrokes(filename)
        words=generateOriginalText(filename)
        print(words)
        if words==' exit':
            print("Bye!\n")
            break 
        else:
           
           telClient.send_telemetry(words)

main()
