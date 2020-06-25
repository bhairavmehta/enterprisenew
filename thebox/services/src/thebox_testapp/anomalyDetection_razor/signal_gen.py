import datetime
import getopt
import sys
import numpy as np
from scipy import signal
import pandas as pd
from sklearn.preprocessing import StandardScaler
from thebox.pubsub_kafka.pubsubkafka import PubSubManagerKafka, PubSubProducer, PubSubConnectionKafka
from thebox.common.abstractmessage import AbstractMessage
from thebox.messages.inferencemessage import InferenceMessage, InferenceDataFeature
import os
import time

class DataProcessor():

    def __init__(self):
        self.timesteps = 1
        self.input_dim = 1
        self.num_sensors = 10
        self.signal_len = 2000
        self.train_data_frame = pd.DataFrame()
        self.test_data_frame = pd.DataFrame()
        
        self.standard_scaler_dict = {}
        self.train_data = np.zeros((self.signal_len, self.num_sensors))
        self.test_data = np.zeros((self.signal_len, self.num_sensors))

    def generate_data(self):
        noise_scale = 10
        t = np.linspace(0, self.signal_len, self.signal_len)

        for idx in range(self.num_sensors):
    
            #sample sensor parameters
            signal_type = np.random.randint(low=0, high=3, size=1)[0]
            signal_amplitude = np.random.randint(low=1, high=100, size=1)[0]
            signal_frequency = np.random.randint(low=5, high=20, size=1)[0]
            signal_phase = np.random.randint(low=1, high=10, size=1)[0]
            signal_offset = np.random.randint(low=-20, high=20, size=1)[0]
            signal_noise = np.random.normal(1, noise_scale, len(t))[0]
    
            #create sensor signal
            if (signal_type == 0):
                sensor = signal_amplitude*signal.square(2*np.pi*signal_frequency*t + signal_phase) + signal_offset + signal_noise
            elif (signal_type == 1):
                sensor = signal_amplitude*np.sin(2*np.pi*signal_frequency*t + signal_phase) + signal_offset + signal_noise
            else:
                sensor = signal_amplitude*signal.sawtooth(2*np.pi*signal_frequency*t + signal_phase) + signal_offset + signal_noise
            #end if
    
            #sample anomaly parameters
            anomaly_type = np.random.randint(low=0, high=2, size=1)[0]
            anomaly_idx = np.random.randint(low=0.2*len(t), high=0.8*len(t), size=1)[0]
            anomaly_magnitude = np.random.randint(low=0.2*signal_amplitude, high=signal_amplitude, size=1)[0]
            anomaly_frequency = np.random.randint(low=signal_frequency, high=2*signal_frequency, size=1)[0]
            anomaly_phase = np.random.randint(low=signal_phase, high=2*signal_phase, size=1)[0]
            anomaly_offset = signal_offset + np.random.randint(low=0, high=20, size=1)[0]
            anomaly_noise = signal_noise + np.random.normal(1, noise_scale, len(t))[0]
            anomaly_window_size = np.random.randint(low=100, high=200, size=1)[0]
            anomaly_window_std = np.random.randint(low=100, high=200, size=1)[0]
    
            #create anomaly signal
            sensor_anomaly = np.copy(sensor)
            if (anomaly_type == 0):
                anomaly = anomaly_magnitude * signal.gaussian(anomaly_window_size, std=anomaly_window_std)
                sensor_anomaly[anomaly_idx:anomaly_idx+anomaly_window_size] += anomaly
            elif (anomaly_type == 1 and signal_type == 0):
                sensor_anomaly[anomaly_idx:-1] = anomaly_magnitude*signal.square(2*np.pi*anomaly_frequency*t[anomaly_idx:-1] + anomaly_phase) + anomaly_offset + anomaly_noise
            elif (anomaly_type == 1 and signal_type == 1):
                sensor_anomaly[anomaly_idx:-1] = anomaly_magnitude*np.sin(2*np.pi*anomaly_frequency*t[anomaly_idx:-1] + anomaly_phase) + anomaly_offset + anomaly_noise
            elif (anomaly_type == 1 and signal_type == 2):
                sensor_anomaly[anomaly_idx:-1] = anomaly_magnitude*signal.sawtooth(2*np.pi*anomaly_frequency*t[anomaly_idx:-1] + anomaly_phase) + anomaly_offset + anomaly_noise
            #end if

            col_name = 'sensor' + str(idx)
            self.train_data_frame[col_name] = sensor
            self.test_data_frame[col_name] = sensor_anomaly
        #end for

    def create_dataset(self, dataset, look_back=64, step=1):
        dataX, dataY = [], []
        for i in range(0, len(dataset)-look_back-1, step):
            dataX.append(dataset[i:(i+look_back),:])
            dataY.append(dataset[i+look_back,:])

        return np.array(dataX), np.array(dataY)

    def preprocess_data(self):

        self.generate_data()

        for idx in range(self.num_sensors):

            key = 'data_scaler_' + str(idx)
            col_name = 'sensor' + str(idx)
    
            data_scaler = StandardScaler()
            data_scaler.fit(self.train_data_frame[col_name].values.reshape(-1,1))

            train_data_scaled = data_scaler.transform(self.train_data_frame[col_name].values.reshape(-1,1))
            test_data_scaled = data_scaler.transform(self.test_data_frame[col_name].values.reshape(-1,1))
    
            self.standard_scaler_dict[key] = data_scaler
            self.train_data[:,idx] = train_data_scaled.flatten()
            self.test_data[:,idx] = test_data_scaled.flatten()
        #end for

        X_test, y_test = self.create_dataset(self.test_data, look_back=64, step=1)  #look_back = window_size #step = window_overlap
        
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
    topic = "in_topic_ad_multi_sensors_infer_test"
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
