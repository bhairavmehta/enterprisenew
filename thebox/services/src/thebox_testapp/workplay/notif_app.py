import sys
import getopt
from thebox.pubsub_kafka.pubsubkafka import PubSubManagerKafka, PubSubProducer, PubSubConnectionKafka
from thebox.messages.notificationmessage import NotificationMessage
from tkinter import *
import threading
from PIL import ImageTk, Image

def printhelp():
    help = """
Usage:
    python notif_app.py -s <server_host:server_port> -t <notification_topic>
"""
    print(help)

class program:

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

        print("Received thread termination request. Bailing out.")
            

    def main(self):
        # main thread will deal with window messaging
        window = Tk()
        window.title("My Naive Listener App")
        window.geometry('400x400')

        lbl = Label(window, text="Start Listening for Work/Play Notifications ...") 
        lbl.grid(column=0, row=0)

        img_work = ImageTk.PhotoImage(Image.open("work.jpg"))
        img_play = ImageTk.PhotoImage(Image.open("play.jpg"))
        
        # start side thread on listening to notification
        def handle_callback(notif_id: str):
            if "doing_work" in notif_id:
                lbl.configure(text="Work", image=img_work)
            else:
                lbl.configure(text="Play", image=img_play)
        
        t = threading.Thread(target=self.signal_thread, args=(handle_callback,))
        t.start()
        
        window.mainloop()

        self.terminating_thread = True
        t.join()


def main():
    pubsub_endpoint = "localhost:10001"
    topic = "out_topic_wp_notif_test"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:t:", ["server=", "topic="])
    except getopt.GetoptError:
        printhelp()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            printhelp()
            sys.exit()
        elif opt in ("-s", "--server"):
            pubsub_endpoint = arg
        elif opt in ("-t", "--topic"):
            topic = arg

    # print out configs
    print(f"Endpoint: {pubsub_endpoint}")
    print(f"Topic: {topic}")

    # run the program
    prog = program(pubsub_endpoint, topic)
    prog.main()

main()