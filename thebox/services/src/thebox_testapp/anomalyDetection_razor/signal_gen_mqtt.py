import datetime
import getopt
import sys
import numpy as np
from scipy import signal
from cycler import cycler
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from thebox.pubsub_kafka.pubsubkafka import PubSubManagerKafka, PubSubProducer, PubSubConnectionKafka
from thebox.common.abstractmessage import AbstractMessage
from thebox.messages.inferencemessage import InferenceMessage, InferenceDataFeature
import os
import time
import paho.mqtt.client as mqtt

class KafkaMessageSender():

    def __init__(self, pubsub_endpoint: str, topic: str):
        self.kafka_mgr = PubSubManagerKafka(PubSubConnectionKafka(pubsub_endpoint))
        # uncomment following code to reset kafka db
        #self.kafka_mgr.reset()
        #time.sleep(1000)
        self.producer = self.kafka_mgr.create_producer(topic, "testapp_sig_gen")
        self.data = np.zeros([1,64,10])
        self.data_delta = {
            "mhhd_s1" : 0.0,
            "mhhd_s2" : 0.0,
            "mhhd_s3" : 0.0,
            "sesor3" : 0.0,
            "sesor4" : 0.0,
            "sesor5" : 0.0,
            "sesor6" : 0.0,
            "sesor7" : 0.0,
            "sesor8" : 0.0,
            "sesor9" : 0.0
        }
        self.interval_begin = datetime.datetime.now()

    def send_signal(self):
        msg = InferenceMessage(
            AbstractMessage.create_new_correlation_id(),
            data_descriptor_name="demo app message",
            feature_data=[
                InferenceDataFeature("input_sequence", self.data[0,:,:])
            ])
        self.producer.publish(msg)
        self.displayData()
        print(f"Message sent! {msg}")

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))
        count = str(msg.payload).split("-")[-1:][0]
        if(count[-1] == '\''):
            count = count[:-1]
        self.data_delta[msg.topic] += float(count)
        new_time = datetime.datetime.now()
        time_delta = new_time-self.interval_begin
        #DEBUG
        #print(time_delta)
        #DEBUG END
        if(time_delta.seconds >= 1):
            data_delta_array = np.array([val for val in self.data_delta.values()])
            # # DEBUG
            # print(data_delta_array)
            # print("shape of delta_array" + str(data_delta_array.shape))
            # print("shape of data" + str(self.data.shape))
            # #DEBUG END
            self.data = np.append([[data_delta_array]],self.data[:,:63,:] ,axis=1)
            # #DEBUG
            # print("merged shape of data" + str(self.data.shape))
            #print(self.data)
            # #DEBUG END
            self.interval_begin = datetime.datetime.now()
            
            self.send_signal()
            self.data_delta = {
            "mhhd_s1" : 0.0,
            "mhhd_s2" : 0.0,
            "mhhd_s3" : 0.0,
            "sesor3" : 0.0,
            "sesor4" : 0.0,
            "sesor5" : 0.0,
            "sesor6" : 0.0,
            "sesor7" : 0.0,
            "sesor8" : 0.0,
            "sesor9" : 0.0
        }


    def MQTTMessaging(self):

        client = mqtt.Client()
        
        client.connect("localhost", 1834, 60)
        client.subscribe("mhhd_s1")
        client.subscribe("mhhd_s2")
        client.subscribe("mhhd_s3")

        client.on_connect = self.on_connect
        client.on_message = self.on_message
        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        client.loop_forever()


    def displayData(self):
        plt.clf()
        # Create data points and offsets
        x = np.linspace(0.0,64, 64)
        y = self.data[0,:,:]
        label = ["Sensor1", "Sensor2", "Sensor3"]
        # Set the plot curve with markers and a title
        for i in range(3):
            plt.plot(x,y[:,i],label=label[i])

        plt.xlim(left = 0, right = 65)
        plt.ylim(bottom = 0, top = 100)
        plt.xlabel("Time")
        plt.ylabel("Sensor Reading")
        plt.title("Readings From Sensor")
        plt.legend()
        plt.show(block=False)
        plt.pause(0.1)

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

    kafkaSender = KafkaMessageSender(pubsub_endpoint, topic)

    print(f"Connected to TheBox at endpoint: {pubsub_endpoint}:{topic}")
    print(f"\n")
    print("===================================================\n")

    kafkaSender.MQTTMessaging()

main()