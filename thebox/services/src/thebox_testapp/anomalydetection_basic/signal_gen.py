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

class TelemetryClient():

    def __init__(self, pubsub_endpoint: str, topic: str):
        self.kafka_mgr = PubSubManagerKafka(PubSubConnectionKafka(pubsub_endpoint))
        self.producer = self.kafka_mgr.create_producer(topic, "testapp_sig_gen")
        self.params = {'dim':1, 'sequence_length':37, 'noise_scale':0.05, 'mixed_sample_size':1, 'anomaly_magnitude':0.5, 'anomaly_window_size':13}
        self.sequence = np.zeros((self.params['dim'],self.params['sequence_length']))
        self.abnormal_peak = np.zeros((self.params['dim'],self.params['sequence_length'] + self.params['anomaly_window_size']))
        self.time = 0
 
    def get_normal_reading(self, dim, sequence_length, noise_scale, time_t, **kwargs):
        """
        Generate one normal reading and push to the existing normal part of the sequence. Push out the old one.
        """
        w = np.linspace(2.6, 5.8, dim) # frequency
        s = np.linspace(1.2, 9.4, dim)  # phase
        reading = []
        for i in range(dim):
            signal = np.sin(w[i]*time_t*0.02 + s[i])
            noise = np.random.normal(0, noise_scale)
            reading.append( signal + noise )
            reading = [np.array(reading)]
        self.sequence = np.append(reading,self.sequence[:,:36] ,axis=1)

    def get_abnormal_reading(self):
        """
        Push 0 to the existing abnormal part of the sequence. Push out the old one.

        """
        abnormal_sequence_length = self.params['anomaly_window_size'] + self.params['sequence_length']
        self.abnormal_peak = np.append(np.zeros((self.params['dim'], 1)), self.abnormal_peak[:,:abnormal_sequence_length-1],axis=1)


    def add_abnormal_peak_to_bank(self):
        """
        Push a list of abnormal data to the data sequence.
        """
        anomaly_magnitude = 1
        window_size = self.params['anomaly_window_size']
        window_std = 2 # anomaly standard deviation
        anomaly_dim = 0
       
        anomaly =  anomaly_magnitude * signal.gaussian(window_size, std=window_std)
        self.abnormal_peak[:,0:window_size] = anomaly

    def send_signal(self, usrInput:str):
        if usrInput == "Y":
            self.add_abnormal_peak_to_bank()
        self.get_normal_reading(time_t = self.time, **self.params)
        self.get_abnormal_reading()
        self.time = self.time + 1

        # combine normal part and abnormal part of the sequence together.
        combined_sequence = self.abnormal_peak[:, self.params['anomaly_window_size']:] + self.sequence

        # the model need to transform multitple dimentional data into one dimention. Flattern the data here.
        sequence_flatten = np.reshape(combined_sequence, (np.prod(combined_sequence.shape)))
        msg = InferenceMessage(
            AbstractMessage.create_new_correlation_id(),
            data_descriptor_name="demo app message",
            feature_data=[
                InferenceDataFeature("input_sequence", sequence_flatten)
            ])

        self.producer.publish(msg)
        displayData(sequence_flatten)
        print(f"Message sent! {msg}")

def printhelp():
    help = """
Usage:
    python signal_gen.py -i <path_to_input_image> -s <server_host:server_port> -t <ingestion_topic>
"""
    print(help)

def displayData(input:np.array):

    plt.clf()
    # Create data points and offsets
    x = np.linspace(0.0,37, 37)
    y = input
    # Set the plot curve with markers and a title
    plt.plot(x,y,'go-')
    plt.xlim(left = 0, right = 37)
    plt.ylim(bottom = -2, top = 2)
    plt.xlabel("Time")
    plt.ylabel("Sensor Reading")
    plt.title("Readings From Sensor")
    plt.show(block=False)
    plt.pause(0.1)

def render_windows_nonblocking_console(telClient : TelemetryClient):
    # Credit: https://stackoverflow.com/questions/2408560/python-nonblocking-console-input
    import msvcrt

    done = False
    while not done:
        telClient.send_signal("N")
        time.sleep(0.1)
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'y':
                telClient.send_signal("Y")
            elif key == b'q':
                sys.exit()
            done = True


def render_linux_nonblocking_console(telClient :TelemetryClient):
    # Credit: https://stackoverflow.com/questions/2408560/python-nonblocking-console-input
   
    import select
    import tty
    import termios

    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        while 1:
            telClient.send_signal("N")
            if (select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])):
                key = sys.stdin.read(1)               
                if key == 'y':
                    telClient.send_signal("Y")
                elif key == 'q':
                    sys.exit()
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


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
    print(f"\n")
    print(f"Sensor will keep sending normal data to the box every 0.1 second\n")
    print(f"Input Y if you want to inset abnormal data the box...\n")
    print("===================================================\n")

    while True:    # infinite loop
        if os.name == "nt":
            render_windows_nonblocking_console(telClient);
        else:
            render_linux_nonblocking_console(telClient)

main()