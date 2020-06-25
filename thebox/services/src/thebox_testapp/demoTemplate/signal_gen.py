import datetime
import getopt
import sys
import numpy as np

from thebox.pubsub_kafka.pubsubkafka import PubSubManagerKafka, PubSubProducer, PubSubConnectionKafka
from thebox.common.abstractmessage import AbstractMessage
from thebox.messages.inferencemessage import InferenceMessage, InferenceDataFeature

class TelemetryClient():

    def __init__(self, pubsub_endpoint: str, topic: str):
        self.kafka_mgr = PubSubManagerKafka(PubSubConnectionKafka(pubsub_endpoint))
        self.producer = self.kafka_mgr.create_producer(topic, "testapp_sig_gen")
    
    # example input: '09/13/2019 11:30 PM'
    def getDayTime(self, s: str):
        s = s.split()

        date = s[0].split("/")
        day = datetime.date(int(date[2]), int(date[0]), int(date[1])).weekday()

        hour = int(s[1].split(":")[0])
        if s[2] == 'PM':
            hour += 12
        return np.array([day, hour]).astype(np.float32)


    def send_telemetry(self, dateTime: str):
        dateTimeFeature = self.getDayTime(dateTime)

        msg = InferenceMessage(
            AbstractMessage.create_new_correlation_id(),
            data_descriptor_name="demo app message",
            feature_data=[
                InferenceDataFeature("float_input", dateTimeFeature)
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


    pubsub_endpoint = "localhost:9092"
    topic = "in_topic_infer_test"
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
    print("Now imagine the date and time is somehow being provided (type 'exit' to quit)...\n")
    print("===================================================\n")
    while True:    # infinite loop
        dateTime = input("DateTime: ")
        if dateTime == "exit":
            print("Bye!\n")
            break 
        else:
            telClient.send_telemetry(dateTime)
    

main()