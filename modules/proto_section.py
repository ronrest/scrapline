"""
GENERIC PROTO-SECTION CLASS
"""
import os
import json
import queue
import time
import threading
import logging
logger = logging.getLogger('myscraper.modules')

# from support.debug import pretty_error_str
# from support.threads import ProtoWorkerThread
from . workers import WorkerGroup
from .. support.datetimefuncs import now_string

# EXCEPTIONS
# connection to database error
# insertion error
# from queue import Empty as EmptyQueueError

# ##############################################################################
#                                 SETTINGS
# ##############################################################################
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f UTC"

def str2file(s, f, mode="w"):
    """ write a string to file"""
    with open(f, mode=mode) as fileobj:
        fileobj.write(s)


class ProtoSection(object):
    def __init__(self, client=None, input_q=None, n_workers=1, worker_prefix="StorerThread", **kwargs):
        self.client = client
        self.input_q = input_q if input_q is not None else queue.Queue()

        self.max_buffer_size = kwargs.get("max_buffer_size", 128)
        self.output_q = queue.Queue(maxsize=self.max_buffer_size)
        # self.output_q = output_q if output_q is not None else queue.Queue()

        # COUNTERS
        self.counter_lock = threading.Lock()
        self.num_items = 0          # number of desired items seen
        self.num_filtered = 0       # number of undesired items seen

        self.date_format = kwargs.get("date_format", DEFAULT_DATE_FORMAT)
        self.tz = "UTC"
        self.print_lock = threading.Lock()  # lock for printing

        # LOGS AND OUTPUT FILES
        self.health_file_lock = threading.Lock()
        self.health_file = kwargs.get("health_file", "health.json")
        self.health_as_json = kwargs.get("health_as_json", True)
        self.last_item = None

        # Process workers group and threads
        self.worker_prefix = worker_prefix
        self._n_workers = n_workers
        self.workers = WorkerGroup(name="Workers")
        self.initialize_worker_threads()

    def initialize_worker_threads(self):
        assert False, "`initialize_worker_threads` needs to be implemented"

    @property
    def status(self):
        if self.is_running:
            return "running"
        elif self.is_finished:
            if self.workers.all_failures:
                return "fail"
            else:
                return "success"
        else:
            return "unknown"

    @property
    def n_workers(self):
        return self.workers.n_workers

    @property
    def is_finished(self):
        return self.workers.all_finished

    @property
    def is_running(self):
        return self.workers.is_running

    def connect(self):
        self.health2file()
        assert False, "Must implement `connect()`"

    def start(self):
        """ Start workers - Continuously poll queue and push to store client """
        try:
            logger.info("STARTING workers from {}".format(self.workers.name))
            self.workers.start()
        finally:
            self.health2file()

    def restart(self):
        assert False, "Restart is not implemented yet"
        # self.health2file()

    def stop(self, i=None, lock=False):
        """ Sends a stop signal to the worker threads, to stop on their
            next refresh cycle.
        Args:
            i:  (int | None)(default=None)
                isolate a specific thread number to close.
                `None` closes all threads.
            lock: (bool)(default=False)
                Should the current thread halt untill all worker threads
                are actually stopped?
        """
        self.workers.stop(i=i, lock=lock)
        self.health2file()

    def finalize(self):
        """ wait till items in the queue are flushed out then stop threads """
        assert False, "FInalize is not implemented yet"
        # self.health2file()

    def disconnect(self):
        assert False, "Disconnect is not implemented yet"
        # self.health2file()

    def get_input_item(self, timeout=None):
        # get from input queue
        try:
            # TODO: infinitely many retries, with a tiemout of just a few
            #       seconds, in a loop to make it responsive to signals
            #       telling it to stop.
            return self.input_q.get(timeout=timeout)
        except:
            raise

    def done_input_item(self):
        """ Send signal to the queue that it has finished processing the item """
        self.input_q.task_done()

    def single_work_step(self):
        assert False, "`single_work_step()` must be implemented"


    @property
    def health_dict(self):
        health = {}
        health["last_update"] =  now_string(format="%Y-%m-%d %H:%M:%S", tz="Australia/Melbourne")
        health["status"] = self.status
        health["is_running"] = self.is_running
        health["is_finished"] = self.is_finished
        health["worker_status"] = self.workers.status
        health["worker_alive_status"] = self.workers.alive_status
        health["worker_is_running"] = self.workers.is_running
        health["worker_all_finished"] = self.workers.all_finished
        health["worker_all_success"] = self.workers.all_success
        health["worker_has_nones"] = self.workers.has_nones
        health["worker_has_failures"] = self.workers.has_failures
        health["input_q"] = self.input_q.qsize()
        health["output_q"] = self.output_q.qsize()
        health["num_items"] = self.num_items
        health["num_filtered"] = self.num_filtered
        health["client_connected"] = "NA"  # self.client.is_connected
        # client health?
        return health

    def health_str(self, as_json=None):
        if as_json is None:
            as_json = self.health_as_json
        if as_json:
            return json.dumps(self.health_dict, indent=4)
        else:
            template = "LAST UPDATE: {last_update}\nIS RUNNING: {is_running}\nIS FINISHED: {is_finished}\nBUFFER QUEUE SIZE: {input_q}\nCLIENT CONNECTED: {client_connected}\nWORKER STATUS: {worker_status}\nWORKER ALIVE: {worker_alive_status}"
            return template.format(**self.health_dict)

    def health2file(self, as_json=None):
        with self.health_file_lock:
            str2file(s=self.health_str(as_json=as_json), f=self.health_file, mode="w")

    def increment_counter(self, counter_name, val=1):
        """ Increments a counter in a threadsafe way """
        with self.counter_lock:
            if counter_name == "num_filtered":
                self.num_filtered += val
            elif counter_name == "num_items":
                self.num_items += val
            else:
                raise ValueError("Incorrect value must be one of (num_filtered ,num_items)")
