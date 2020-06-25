import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, RegexpTokenizer
from nltk.stem import SnowballStemmer
from keras.preprocessing.text import Tokenizer
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
import getopt
import sys
import os
import numpy as np

from thebox.pubsub_kafka.pubsubkafka import PubSubManagerKafka, PubSubProducer, PubSubConnectionKafka
from thebox.common.abstractmessage import AbstractMessage
from thebox.messages.inferencemessage import InferenceMessage, InferenceDataFeature

class UrlProcessor(object):
    """
    Helper class to process URL data before running inference
    """ 
    num_train: int = 1000000
    dict_file: str = "URL.csv"
    MAX_NB_WORDS = 1e6
    max_token_len: int = 5
    
    @staticmethod
    def get_tokenizer():
        tokenizer_nltk = RegexpTokenizer(r'[a-zA-Z]+')
        stop_words = set(stopwords.words('english'))
        stop_words.update(['http', 'https', 'www', 'com', 'html', 'org', 'ru', 'jp', 'uk', 'ca', '//'])
        return tokenizer_nltk, stop_words
    
    def __init__(self):
        self.tokenizer_nltk, self.stop_words = UrlProcessor.get_tokenizer()
        self.tokenzier_keras = self.cache_url_dict()

    def tokenize(self, raw_url: str):
        url_tokens = self.tokenizer_nltk.tokenize(raw_url)
        url_tokens_clean = [word for word in url_tokens if word not in self.stop_words]
        return url_tokens_clean

    def cache_url_dict(self):
        url_df = pd.read_csv(self.dict_file, header=None)
        url_df.columns = ['index', 'url', 'category']
        url_df.dropna(inplace=True)
        url_train_df = url_df.sample(n=self.num_train, random_state=1)
        raw_docs_train = url_df['url'].apply(lambda u: self.tokenize(u))
        # NOTE: why 2 passes at all?
        processed_docs_train = []
        processed_docs_test = []
        for doc in raw_docs_train:
            tokens = self.tokenizer_nltk.tokenize(" ".join(doc))
            filtered = [word for word in tokens if word not in self.stop_words]
            processed_docs_train.append(" ".join(filtered))
        tokenizer_keras = Tokenizer(num_words=self.MAX_NB_WORDS, lower=True, char_level=False)
        tokenizer_keras.fit_on_texts(processed_docs_train + processed_docs_test)
        word_index = tokenizer_keras.word_index
        print("dictionary size: ", len(word_index))
        return tokenizer_keras
        
    def process_url(self, raw_url: str):
        url_tokens_clean = self.tokenize(raw_url)
        url_seq = self.tokenzier_keras.texts_to_sequences([url_tokens_clean])[0][0:self.max_token_len]
        if len(url_seq) < self.max_token_len:
            url_seq.extend([0] * (self.max_token_len - len(url_seq)))
        return np.array(url_seq).reshape(1,-1)


class AppProcessor(object):
    """
    Helper class to process Application Process data
    """
    
    num_train: int = 1000000
    dict_file: str = "AppResult.csv"
        
    def __init__(self):
        self.encoder = self.cache_app_transform()
    
    def cache_app_transform(self):
    
        app_session_df = pd.read_csv(self.dict_file)
        app_session_df.dropna(inplace=True)

        for i in range (10):
            app_session_df = pd.concat([app_session_df,app_session_df], axis=0)

        # NOTE: seed?
        app_train_df = app_session_df.sample(n=self.num_train, random_state=1)
        #print(app_train_df)
        enc = OneHotEncoder(handle_unknown='ignore', sparse=False)
        enc.fit(app_train_df['Process'].values.reshape(-1,1))

        print(f"Encoder created with category count: {enc.categories_[0].shape}")
        return enc

    def process_app(self, app_name: str):
        return self.encoder.transform(np.array([app_name]).reshape(-1,1))



class TelemetryClient():

    def __init__(self, pubsub_endpoint: str, topic: str):
        self.appProc = AppProcessor()
        self.urlProc = UrlProcessor()
        self.kafka_mgr = PubSubManagerKafka(PubSubConnectionKafka(pubsub_endpoint))
        self.producer = self.kafka_mgr.create_producer(topic, "testapp_sig_gen")
    
    def send_telemetry(self, url: str):
        
        appFeature = self.appProc.process_app("chrome.exe").astype(np.float32)
        urlFeature = self.urlProc.process_url(url).astype(np.float32)

        msg = InferenceMessage(
            AbstractMessage.create_new_correlation_id(),
            data_descriptor_name="demo app message",
            feature_data=[
                InferenceDataFeature("app", appFeature),
                InferenceDataFeature("url", urlFeature)
            ])

        self.producer.publish(msg)
        print(f"Message sent! {msg}")



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
    topic = "in_topic_wp_infer_test"

    nltk.download('stopwords')

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:t:", ["server=", "topic="])
    except getopt.GetoptError:
        printhelp()
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            printhelp()
            sys.exit()
            image_file_path = arg
        elif opt in ("-s", "--server"): # e.g. localhost:9092
            pubsub_endpoint = arg
        elif opt in ("-t", "--topic"):
            topic = arg

    telClient = TelemetryClient(pubsub_endpoint, topic)

    print(f"Connected to TheBox at endpoint: {pubsub_endpoint}:{topic}")
    print("Now imagine you are in the web browser (type 'exit' to quit)...\n")
    print("===================================================\n")
    while True:    # infinite loop
        url = input("Url: ")
        if url == "exit":
            print("Bye!\n")
            break 
        else:
            telClient.send_telemetry(url)
    

main()