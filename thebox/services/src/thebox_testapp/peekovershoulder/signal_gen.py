from PIL import Image
import getopt
import sys
import os
import numpy as np
import time

from thebox.pubsub_kafka.pubsubkafka import PubSubManagerKafka, PubSubProducer, PubSubConnectionKafka
from thebox.common.abstractmessage import AbstractMessage
from thebox.messages.inferencemessage import InferenceMessage, InferenceDataFeature

class TheBoxSignalClient():

    def __init__(self, pubsub_endpoint: str, topic: str):
        self.kafka_mgr = PubSubManagerKafka(PubSubConnectionKafka(pubsub_endpoint))
        self.producer = self.kafka_mgr.create_producer(topic, "testapp_sig_gen")
    
    def send(self, image: np.ndarray):

        print(f"image size: {image.size}")

        msg = InferenceMessage(
            AbstractMessage.create_new_correlation_id(),
            data_descriptor_name="camera_feed_pos_demo",
            feature_data=[
                InferenceDataFeature("image_tensor", image),
            ])

        self.producer.publish(msg)
        print(f"Message sent! {msg}")


def read_image_as_numpy_array(filepath: str):
    # PIL read image already as RGB
    img = np.asarray(Image.open(filepath))
    return img

def printhelp():
    help = """
Usage:
    python signal_gen.py -i <path_to_input_image> -s <server_host:server_port> -t <ingestion_topic> [-i <image>] -c
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
    topic = "in_topic_pos_infer_test"
    static_image = None
    cameraid = 0

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:t:i:c:", ["server=", "topic=", "image=", "cameraid="])
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
        elif opt in ("-i", "--image"):
            static_image = arg
        elif opt in ("-c", "--cameraid"):
            cameraid = int(arg)

    client = TheBoxSignalClient(pubsub_endpoint, topic)

    if static_image is not None:
        print("Working in Static-Image mode:")

        print(f"Reading {static_image} ...")
        test_img = read_image_as_numpy_array(static_image)
        print(f"Image: {test_img.shape}, {test_img.dtype.type}")
        client.send(test_img)

    else:
        print("Working in Video Camera mode:")

        import cv2

        current_milli_time = lambda: int(round(time.time() * 1000))

        print(f"Using camera with id = {cameraid}")
        cap = cv2.VideoCapture(cameraid)
        windowNotSet = True

        lastframetime = current_milli_time()
        throttle = 400 # 2.5 frame per second at max
        frames_sent = 0

        while True:
            ret, image = cap.read()
            if ret == 0:
                break

            [h, w] = image.shape[:2]
            #print (h, w)
            test_image = cv2.flip(image, 1).astype(np.uint8)
            assert(isinstance(image, np.ndarray))

            curtime = current_milli_time()
            if (curtime - lastframetime >= throttle):
                client.send(test_image)
                frames_sent+=1
                lastframetime = curtime
                print(f"f={frames_sent}")

            if windowNotSet is True:
                cv2.namedWindow("tensorflow based (%d, %d)" % (w, h), cv2.WINDOW_NORMAL)
                windowNotSet = False

            cv2.imshow("tensorflow based (%d, %d)" % (w, h), test_image)
            k = cv2.waitKey(1) & 0xff
            if k == ord('q') or k == 27:
                break

    
    print("All done.")

main()