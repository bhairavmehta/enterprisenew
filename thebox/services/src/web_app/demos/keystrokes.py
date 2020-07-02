import pickle
import numpy as np
import threading
from thebox.pubsub_kafka.pubsubkafka import PubSubManagerKafka, PubSubConnectionKafka
from thebox.common.abstractmessage import AbstractMessage
from thebox.messages.inferencemessage import InferenceMessage, InferenceDataFeature


class KeyStrokes:

    terminating_thread = False

    def __init__(self, pubsub_endpoint, topic):
        self.pubsub_endpoint = pubsub_endpoint
        self.topic = topic
        self.thread = None
        self.condition = threading.Condition()
        self.data = None

    def signal_thread(self, terminating_thread):

        kafka_mgr = PubSubManagerKafka(PubSubConnectionKafka(
            self.pubsub_endpoint))
        consumer = kafka_mgr.create_consumer(
            [self.topic], "testapp_sig_gen", "testapp")

        print("Starting listening for notifications ...")
        while not terminating_thread():
            (t, o) = consumer.poll(1)
            if o is not None:
                print(terminating_thread())
                if o.notification_id == 'is_not_me':
                    self.data = 'not_me'
                else:
                    self.data = 'me'
                with self.condition:
                    self.condition.notifyAll()

    def wait(self):
        print('waiting')
        with self.condition:
            self.condition.wait()
        print('freed')

    def run(self):

        self.thread = threading.Thread(target=self.signal_thread, args=(lambda: self.terminating_thread, ))
        self.thread.start()
        return

    def stop(self):
        print('Stopping KeyStrokes app!')
        self.terminating_thread = True
        self.thread.join()
        return


class TelemetryClient:

    def __init__(self, pubsub_endpoint: str, topic: str):
        self.kafka_mgr = PubSubManagerKafka(PubSubConnectionKafka(pubsub_endpoint))
        self.producer = self.kafka_mgr.create_producer(topic, "testapp_sig_gen")

    @staticmethod
    def svm_features(s):
        valid_x = set([])
        valid_x.add(s)
        fi = open('../thebox_testapp/keyStrokes/tfidfvocabulary.pkl', 'rb')

        tfidf_vect = pickle.load(fi)

        xvalid_tfidf1 = tfidf_vect.transform(valid_x)
        xvalid_tfidf = xvalid_tfidf1.toarray()
        return xvalid_tfidf.astype(np.float32)

    def send_telemetry(self, text: str):
        key_stroke_feature = np.squeeze(self.svm_features(text))
        msg = InferenceMessage(
            AbstractMessage.create_new_correlation_id(),
            data_descriptor_name="demo app message",
            feature_data=[
                InferenceDataFeature("float_input", key_stroke_feature)
            ])
        self.producer.publish(msg)
