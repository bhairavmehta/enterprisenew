import datetime
import getopt
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from thebox.pubsub_kafka.pubsubkafka import PubSubManagerKafka, PubSubProducer, PubSubConnectionKafka
from thebox.common.abstractmessage import AbstractMessage
from thebox.messages.inferencemessage import InferenceMessage, InferenceDataFeature
import os
import time

class DataProcessor():
    
    train_data_file = "art_daily_no_noise.csv"
    test_data_file = "art_daily_jumpsup.csv"

    def __init__(self):
        self.timesteps = 1
        self.input_dim = 1

    def create_dataset(self, dataset, look_back=64):
        dataX, dataY = [], []
        for i in range(len(dataset)-look_back-1):
            dataX.append(dataset[i:(i+look_back),:])
            dataY.append(dataset[i+look_back,:])

        return np.array(dataX), np.array(dataY)

    def preprocess_data(self):
        
        train_df = pd.read_csv(self.train_data_file)
        test_df = pd.read_csv(self.test_data_file)

        data_scaler = StandardScaler()
        data_scaler.fit(train_df[['value']].values)
        
        train_data = data_scaler.transform(train_df[['value']].values)
        test_data = data_scaler.transform(test_df[['value']].values)

        X_test, y_test = self.create_dataset(test_data, look_back=64)  #look_back = window_size
        
        self.timesteps = X_test.shape[1]
        self.input_dim = X_test.shape[-1]

        return X_test


class TelemetryClient():

    def __init__(self, pubsub_endpoint: str, topic: str):
        self.data_proc = DataProcessor()
        self.kafka_mgr = PubSubManagerKafka(PubSubConnectionKafka(pubsub_endpoint))
        self.producer = self.kafka_mgr.create_producer(topic, "testapp_sig_gen")

    def send_telemetry(self):
    
        X_test = self.data_proc.preprocess_data()
        num_data = X_test.shape[0]

        for idx in range(num_data):

            msg = InferenceMessage(
                AbstractMessage.create_new_correlation_id(),
                data_descriptor_name="demo app message",
                feature_data=[
                    InferenceDataFeature("input_sequence", X_test[idx,:])
                ])

            self.producer.publish(msg)
            print(f"Message sent! {msg}")
        #end for            

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


    pubsub_endpoint = "localhost:9092"
    topic = "in_topic_ad_infer_test"
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
        cmd = input("cmd: ")
        if cmd == "exit":
            print("Bye!\n")
            break 
        else:
            telClient.send_telemetry()
    

main()
