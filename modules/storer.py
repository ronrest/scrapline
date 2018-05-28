"""
GENERIC STORER OBJECT
"""
import time
import json
import queue
import threading
import logging
logger = logging.getLogger('scraper_pipeline.storer')

# from .. support.debug import pretty_error_str
# from .. support.threads import ProtoWorkerThread
# from .. support.threads import WorkerGroup
# from support.misc import now_string

from . proto_section import ProtoSection
from . workers import ProtoWorkerThread
from .. support.datetimefuncs import timestamp2str, now_string
from .. support.debug import pretty_error_str


# EXCEPTIONS
# connection to database error
# insertion error
from queue import Empty as EmptyQueueError


# ##############################################################################
#                                     SUPPORT
# ##############################################################################
def str2file(s, f, mode="w"):
    """ write a string to file"""
    with open(f, mode=mode) as fileobj:
        fileobj.write(s)


# ##############################################################################
#                                   STORE WORKER
# ##############################################################################
class MyWorker(ProtoWorkerThread):
    def work(self, single_work_step):
        while True:
            if self.stop_signal:
                self.status = "success"
                break
            try:
                single_work_step()
                # time.sleep(3)
            except:
                # URGENT: TODO: catch netowrk errors
                # TODO: store failed objects in a file or failed queue
                # self.health_monitor.health2file()
                # TODO: email alarm
                # TODO: sms alarm
                # TODO: Add message to failures file, or queue to manually upload.
                # TODO: Add to health monitor
                msg = "HAD TROUBLE STORING ITEM IN DATABASE"
                logger.warning(pretty_error_str(msg))

        if self.status != "success":
            self.status = "fail"


# ##############################################################################
#                                        STORER
# ##############################################################################
class Storer(ProtoSection):
    def __init__(self, client, input_q, n_workers=1, worker_prefix="StorerThread", **kwargs):
        ProtoSection.__init__(self, client=client, input_q=input_q, n_workers=n_workers, worker_prefix=worker_prefix, **kwargs)

        # self.workers = WorkerGroup(name="StorerWorkers")

        self.n_retries = 5
        self.wait_before_retry = 5

        self.monitor_file_lock = threading.Lock()
        self.monitor_file = kwargs.get("monitor_file", "storer_monitor.log")
        self.health_file = kwargs.get("health_file", "health_storer.json")
        self.last_item = None

    def initialize_worker_threads(self):
        self.workers.clear()
        for i in range(self._n_workers):
            worker_name = "{}_{}".format(self.worker_prefix, i)
            self.workers.append(MyWorker(name=worker_name, single_work_step=self.single_work_step))
        self.health2file()

    def connect(self):
        self.client.connect()
        self.health2file()

    def store(self, item):
        # send to storer client
        # TODO: multiple retries, so long as the error message received is
        #       on the server side of things, or connection issue.
        # if max retries reached, raise a max retries error.
        # if other error enocuntered raise that error as well.
        self.client.store(item)
        self.last_item = item

    def single_work_step(self):
        try:
            # item = self.get_input_item(timeout=1)
            item = self.get_input_item(timeout=0.5)
            assert isinstance(item, dict), "Item being passed to storer should be a dictionary object"
            self.store(item)
            self.feedback(item)
            self.increment_counter("num_items")
            self.last_item = item
            self.done_input_item()
        except EmptyQueueError:
            None
        except AssertionError:
            self.done_input_item()
            raise
        except:
            self.done_input_item()
            msg = "HAD TROUBLE STORING ITEM IN DATABASE:\n{}".format(json.dumps(item, indent=4))
            logger.warning(pretty_error_str(msg))
            raise
        finally:
            # TODO: test to see if this is executed, even when exceptions are raised
            self.health2file()

    def feedback_str(self, item):
        self.feedback_template = "{id} [{time}] {text_short}\n"
        return self.feedback_template.format(text_short=item["text"][:20], **item)

    def feedback(self, item):
        # TODO: maybe keep around the last few messages
        with self.monitor_file_lock:
            str2file(s=self.feedback_str(item), f=self.monitor_file, mode="w")
