import json
import threading
import os
import sys
import signal
import time
from typing import List
from time import sleep

from thebox.common.config import Config
from thebox.common.pubsub import PubSubManager, PubSubConsumer
from thebox.common.abstractmessage import AbstractMessage

from .logging import acquire_service_logger


def or_set(self):
    self._set()
    self.changed()


def or_clear(self):
    self._clear()
    self.changed()


class OrEvent():
    """Or-ify event so that it would trigger on any of the event provided
       References:
       - https://stackoverflow.com/questions/12317940/python-threading-can-i-sleep-on-two-threading-events-simultaneously
    """

    def orify(e, changed_callback):
        e._set = e.set
        e._clear = e.clear
        e.changed = changed_callback
        e.set = lambda: or_set(e)
        e.clear = lambda: or_clear(e)

    def __init__(self, events: List, handler=None):

        self.or_event = threading.Event()

        def changed():
            bools = [e.is_set() for e in events]
            if any(bools):
                self.or_event.set()
                if handler is not None:
                    handler(events)
            else:
                self.or_event.clear()

        for e in events:
            OrEvent.orify(e, changed)
        changed()


class ThreadEx(threading.Thread):
    """Enhanced version of the thread that would propagate
       exception caught during execution
    """

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, daemon=None):
        self.exception: BaseException = None
        self.exception_event: threading.Event = threading.Event()
        super().__init__(group=group, target=target, name=name,
                         args=args, kwargs=kwargs, daemon=daemon)

    def run(self):
        """Overriding default run() method to catch any exception
            thrown and store it in the self.exception. See following links:
            https://github.com/python/cpython/blob/master/Lib/threading.py 
            https://stackoverflow.com/questions/2829329/catch-a-threads-exception-in-the-caller-thread-in-python/12223550#12223550
        """
        try:
            super().run()
        except BaseException as e:
            self.exception = e
            self.exception_event.set()

    def join(self):
        """Overriding default join call that would re-thrown the exception
        """
        super().join()
        if self.exception is not None:
            raise self.exception


class BaseService(object):

    def __init__(self):
        self.log = acquire_service_logger()

    def startThread(self, target, args: List, daemon: bool = None) -> ThreadEx:
        """Create a new thread wrapped in exception catching thread helper"""
        return ThreadEx(target=target, args=args, daemon=daemon)


class BaseWorkerService(BaseService):
    """Base class of a micro services
       The class implements the communications with pubsub pipeline and
       maintains two message loops, one for orchestration and one for
       scenario specific messages.
       The child class (real microservice) should implement handler for 
       two type of messages
    """

    # frequency of polling retry
    PULL_INTERVAL_DEFAULT = 10

    # the channel that the orchestrator calls this service
    ORCHESTRATION_GROUP_NAME = "default_orchestration_group"

    def __init__(self, orch_topic: str, pubsub_manager: PubSubManager, client_name: str = None):

        self.__orchestration_topic = orch_topic
        self.__pubsub_mgr = pubsub_manager
        self.__client_name = str(
            id(self)) if client_name is None else client_name

        self.__pull_interval = self.PULL_INTERVAL_DEFAULT
        self.__orchestration_group = self.ORCHESTRATION_GROUP_NAME

        self.__reset_topics = True
        self.__reset_topics_lock = threading.Lock()
        self.__kill_signal = False
        self.__kill_signal_lock = threading.Lock()
        self.__wait_kill_event = threading.Event()

        self.orch_thread = None
        self.scn_thread = None
        self.or_event = None

        super().__init__()

    def start(self, wait=False) -> None:
        """Start the workder service. It spaws orchestrator
        thread and scenario processing thread. Both threads
        will wait for incoming message from designated topics.

        To designate topics for scenario processing to listen 
        to, see update_scenario_topics.

        To desginate topic for orchestration, the child class
        need to init the base class for the orch_topic parameter.


        Keyword Arguments:
            wait {bool} -- If true, will block until both threads
            are killed (default: {False})

        Raises:
            Exception: If threads cannot be started due to pending
            termination, an exception will be thrown.
        """
        canStartThread = True
        if (not self.__kill_signal):
            with self.__kill_signal_lock:
                if (not self.__kill_signal):

                    assert((self.orch_thread is None) ==
                           (self.scn_thread is None))

                    if (self.orch_thread is None):
                        # starting the orchestration listeners
                        self.orch_thread: ThreadEx = self.startThread(
                            target=self.__thread_orchestration_listener, args=("orchestration_thread",), daemon=True)
                        self.orch_thread.start()

                    # starting per-scenario channel listeners
                    if (self.scn_thread is None):
                        self.scn_thread: ThreadEx = self.startThread(
                            target=self.__thread_scenario_listeners, args=("scenarios_thread",), daemon=True)
                        self.scn_thread.start()

                    self.or_event = OrEvent(
                        [self.orch_thread.exception_event,
                            self.scn_thread.exception_event],
                        self.__exception_event_handler)
                    
                    self.log.debug(
                        "All threads started successfully. Now waiting for incoming messages ...")

                else:
                    # in the processing of killing threads
                    canStartThread = False

        if (not canStartThread):
            self.log.error("Cannot start as old threads are still running ...")
            raise Exception(
                "Cannot start new threads as old threads are in the process of being killed")

        if wait:
            self.waittostop()

    def __signal_handler(self, signal, frame) -> None:
        """Handler for signal.SIGINT (mostly Ctrl+C keyboard interrupt)"""
        self.log.debug("Received termination signal, terminating ...")
        self.__wait_kill_event.set()

    def __windows_signal_handler(self, dwCtrlType) -> int:
        """Wrapper for __singal_handler for Microsoft Windows case"""
        if dwCtrlType == 0:  # CTRL_C_EVENT
            self.__signal_handler(signal.SIGINT, sys._getframe(0))
            return 1  # don't chain to the next handler
        return 0  # chain to the next handler

    def __exception_event_handler(self, exception_events: List[threading.Event]) -> None:
        """Handler for any thread throwning exception"""
        self.log.debug(
            f"Observed exception from at least one worker thread, terminating ...")
        if self.orch_thread.exception_event.is_set():
            self.log.debug(
                f"Exception in Orchestrator Thread: {self.orch_thread.exception}")
        if self.scn_thread.exception_event.is_set():
            self.log.debug(
                f"Exception in Scenario Thread: {self.scn_thread.exception}")
        self.__wait_kill_event.set()

    def waittostop(self) -> None:
        """Wait for keyboard interrupt then call stop()
        This function must be called by main thread.
        """
        if os.name == "nt":
            # Win32 Specific Code to handle the ctrl+c event
            # see this https://stackoverflow.com/questions/15457786/ctrl-c-crashes-python-after-importing-scipy-stats
            import win32api
            win32api.SetConsoleCtrlHandler(self.__windows_signal_handler, 1)
        else:
            signal.signal(signal.SIGINT, self.__signal_handler)
            self.log.debug("Wait for Ctrl+C to terminate ...")

        self.__wait_kill_event.wait()
        self.stop()

    def stop(self) -> None:
        """Issue stop signal to terminate all running thread
        """

        if not self.__kill_signal:
            self.log.debug("intend to stop the threads ...")
            with self.__kill_signal_lock:
                if (not self.__kill_signal):
                    self.__kill_signal = True
                    self.log.debug("stop all running threads ...")
                    if (self.orch_thread is not None):
                        self.orch_thread.join()
                        self.orch_thread = None
                    if (self.scn_thread is not None):
                        self.scn_thread.join()
                        self.scn_thread = None
                    self.or_event = None
                    self.__kill_signal = False

    def __thread_scenario_listeners(self, thread_name: str) -> None:
        self.log.debug(
            f"Starting Orchestration Listener Thread: {thread_name} ...")

        consumer = None
        topic_w_prod = dict()

        while not self.__kill_signal:

            # check if topics to listen has changed
            reset_topics = False
            if (self.__reset_topics):
                with self.__reset_topics_lock:
                    if (self.__reset_topics):
                        reset_topics = True
                        self.__reset_topics = False

            # read topic listeners and producers
            if (reset_topics):
                topic_w_prod = {
                    t[0]:
                    self.__pubsub_mgr.create_producer(
                        t[1], self.__client_name)
                    for t in self.update_scenario_topics()
                }
                topics_in = list(topic_w_prod.keys())

                if (consumer is None):
                    consumer = self.__pubsub_mgr.create_consumer(
                        topics_in, self.__client_name, self.__orchestration_group)
                else:
                    self.log.debug(
                        f"{thread_name}: Now listening to topics: {topics_in} ...")
                    consumer.reset_topics(topics_in)

            # poll messages forom the listened topics
            if (len(topic_w_prod) > 0):
                msg = consumer.poll(self.__pull_interval)
                if (msg is not None and msg[0] is not None):
                    # handling scenario messages if any
                    self.log.debug(f"{thread_name}: Received message from topic \
                            {msg[0]} ...")
                    result_msgs = self.handle_scenario_message(msg[0], msg[1])
                    assert msg[0] in topic_w_prod
                    if result_msgs is not None and \
                            isinstance(result_msgs, List) and \
                            msg[0] in topic_w_prod:
                        out_topic_prod = topic_w_prod[msg[0]]
                        for res in result_msgs:
                            assert isinstance(res, AbstractMessage)
                            self.log.debug(f"{thread_name}: Sending resulting message to topic" +
                                           f"{out_topic_prod.topic_name} ...")
                            out_topic_prod.publish(res)
            else:
                # if no topics to be listened, simulate a poll time out to avoid spinning too fast
                sleep(self.__pull_interval)

        # clean up
        topic_w_prod.clear()
        consumer.reset_topics([])
        self.log.debug(f"{thread_name}: killed")

    def __thread_orchestration_listener(self, thread_name: str) -> None:
        self.log.debug(f"Starting Orchestration Listener Thread: {thread_name} " +
                       f"with topic {self.__orchestration_topic} ...")
        consumer = self.__pubsub_mgr.create_consumer(
            [self.__orchestration_topic], self.__client_name, self.__orchestration_group)
        # message loop to listen to orchestration messages
        while not self.__kill_signal:
            msg = consumer.poll(self.__pull_interval)
            if msg is not None and msg[0] is not None:
                # handling a new orchestration message
                self.log.debug(
                    f'{thread_name}: Received orchestration message: {msg[1]}')
                self.handle_orchestration_message(msg[1])
                # issue topic subscription resets when needed
                with self.__reset_topics_lock:
                    self.__reset_topics = True
                self.log.debug(
                    f'{thread_name}: Done handling orchestration message.')

        consumer.reset_topics([])
        self.log.debug(f"{thread_name}: killed")

    def handle_orchestration_message(self, msg: AbstractMessage) -> bool:
        """Handles the orchestration message, returns (True or False) if the
           the topic subscriptions need to be changed (typically when succeeded)
           or not (when failed)
        """
        raise NotImplementedError()

    # handle per-scenario message
    def handle_scenario_message(self, topic: str, msg: AbstractMessage) -> List[AbstractMessage]:
        """Handles the per-scenario message
           and return a message, if needed, to be piped in the out-topic in response
        """
        raise NotImplementedError()

    def update_scenario_topics(self) -> List:  # List[(str, str)]:
        """Called when topics need to be renewed, return a list of topic pairs
           each pair has a topic to listen to (usually one topic per scenario),
           and corresponding output topics
        """
        raise NotImplementedError()
