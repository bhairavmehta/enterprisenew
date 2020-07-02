import sys
import getopt
from thebox.pubsub_kafka.pubsubkafka import PubSubManagerKafka, PubSubConnectionKafka
import threading
from web_app.main import app
import signal
import time
import requests


def print_help():
    print("""
        Usage:
            python notif_app.py -s <server_host:server_port> -t <notification_topic>
        """)


class Program:

    terminating_thread = False

    def __init__(self, pubsub_endpoint, topic):
        self.pubsub_endpoint = pubsub_endpoint
        self.topic = topic

    def signal_thread(self, notif_callback):

        kafka_mgr = PubSubManagerKafka(PubSubConnectionKafka(self.pubsub_endpoint))
        consumer = kafka_mgr.create_consumer([self.topic], "testapp_sig_gen", "testapp")

        print("Starting listening for notifications ...")

        while not self.terminating_thread:
            (t, o) = consumer.poll(1)
            if o is not None:
                print(f"Getting message from topic t={t}:")
                print(f"{o}")
                print(f"")
                notif_callback(o.notification_id)

    def main(self):

        # start side thread on listening to notification
        def handle_callback(notif_id: str):
            print(notif_id)
            headers = {
                'Content-type': 'application/json',
            }

            if "is_not_me" in notif_id:
                data = '{"result":"not_me"}'
            else:
                data = '{"result":"me"}'
            response = requests.post('http://127.0.0.1:5000/demos/key-strokes', headers=headers, data=data)
            print(response)
        t = threading.Thread(target=self.signal_thread, args=(handle_callback,))
        frontend_app = threading.Thread(target=app.run, args=())

        def signal_handler(sig, frame):
            print('>>>>>>>>>>>> Interupt')
            self.terminating_thread = True
            response = requests.post('http://127.0.0.1:5000/shutdown',
                                     headers={'Content-type': 'application/json'},
                                     data='{}')
            print(response)
            t.join()
            frontend_app.join()
            exit()
        signal.signal(signal.SIGINT, signal_handler)

        frontend_app.start()
        t.start()

        while True:
            time.sleep(1)


def main():
    pubsub_endpoint = "localhost:10001"
    topic = "out_topic_ks_notif_test"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:t:", ["server=", "topic="])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print()
            sys.exit()
        elif opt in ("-s", "--server"):
            pubsub_endpoint = arg
        elif opt in ("-t", "--topic"):
            topic = arg

    # print out configs
    print(f"Endpoint: {pubsub_endpoint}")
    print(f"Topic: {topic}")

    # app.run()
    prog = Program(pubsub_endpoint, topic)
    prog.main()


if __name__ == "__main__":
    main()
