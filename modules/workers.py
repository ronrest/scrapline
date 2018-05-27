import threading
import logging
logger = logging.getLogger('scraper_pipeline.workers')

# QUEUE_TERMINATING_VALUE = "zzz this is a killer"

# ##############################################################################
#                               WORKER THREAD OBJECT
# ##############################################################################
class ProtoWorkerThread(threading.Thread):
    """
    This is a worker thread class proto object that should be sub-clased.
    You should implement the work() function.
        - In this function you should set control the logic for the status:
        - You should determine under which circumstances you set:
            - self.status = "success"
            - self.status = "fail"
        - the class automatically sets the status to "running" when the
          run() method is called.

    Args:
        name: (str)
            name to give this thread
        **kwags:
            keyword arguments to send to work() function

    Attributes:
        name: (str)
            Name of this thread
        status: (str | None)
            -  None     = has not started yet
            - "running" = in the process of running it worker function
            - "success" = finished running its worker function to completion
            - "fail"   = terminated its worker function early
        _stop_event:
            a flag that you should monitor to make it finish any loops it is
            processing.
    """
    def __init__(self, name="Worker", daemon=True, **kwargs):
        threading.Thread.__init__(self)
        self.name = name
        self.status = None
        self._stop_event = threading.Event()
        self.kwargs = kwargs
        self.daemon = daemon

    @property
    def stop_signal(self):
        return self._stop_event.is_set()

    def work(self, **kwargs):
        assert False, "Work is not implemented yet"
        # while not _stop_event.is_set():
        #     # DO SOME WORK
        # self.status = "success"

    def run(self):
        try:
            self._stop_event.clear()
            self.status = "running"
            self.work(**self.kwargs)
        except:
            raise
        finally:
            if self.status != "success":
                self.status = "fail"

    # # Implementation of thread stopping based on this suggestion in
    # # stackoverflow thread: https://stackoverflow.com/a/325528
    def stop(self):
        logger.info("WORKER {} received stop signal".format(self.name))
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def __str__(self):
        return '<WorkerThread: ("{}" {})>'.format(self.name, self.status)


    def __repr__(self):
        return '<WorkerThread: ("{}" {})>'.format(self.name, self.status)



# ##############################################################################
#                               WORKER GROUP
# ##############################################################################
class WorkerGroup(object):
    """ Object that wraps around a list of thread workers to provide conveneince
        functions about the health of the worker thread objects.

    """
    def __init__(self, workers=None, name="workers"):
        self._workers = workers if workers is not None else list()
        self.name = name

    def start(self, i=None):
        if i is None:
            for worker in self._workers:
                worker.start()
        else:
            assert False, "Starting a specific isolated thread Not implemented yet"

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
        if i is None:
            logger.info("STOPPING all storer worker threads in {}".format(self.name))
            for worker in self._workers:
                worker.stop()
            if lock:
                for worker in self._workers:
                    worker.join()
                logger.debug("STOPPED all worker threads in {}".format(self.name))

        else:
            assert False, "Stopping a specific isolated thread not implemented yet"


    def nullify(self, i=None):
        """ Sets all (or selected worker) threads to None """
        if i is None:
            for i in range(self.n_workers):
                self._workers[i] = None
        else:
            self._workers[i] = None

    def clear(self):
        """ Empties out the threads list """
        self._workers = list()

    @property
    def n_workers(self):
        return len(self._workers)

    @property
    def status(self):
        return [getattr(worker, "status", None) for worker in self._workers]

    @property
    def is_running(self):
        return any([status=="running" for status in self.status])

    @property
    def all_finished(self):
        """ returns """
        return all([(status=="success" or status=="fail") for status in self.status]) and self.n_workers > 0

    @property
    def all_success(self):
        return all([status=="success" for status in self.status]) and self.n_workers > 0

    @property
    def has_failures(self):
        return any([status=="fail" for status in self.status])

    @property
    def all_failures(self):
        return all([status=="fail" for status in self.status])

    @property
    def has_nones(self):
        return any([status is None for status in self.status])

    @property
    def alive_status(self):
        return [worker.is_alive() for worker in self._workers]

    @property
    def has_dead_threads(self):
        return any([not worker.is_alive() for worker in self._workers])

    @property
    def all_threads_alive(self):
        return all([worker.is_alive() for worker in self._workers])

    def __str__(self):
        return str(self._workers)

    def __repr__(self):
        return '<WorkerGroup: ("{}" {})>'.format(self.name, str(self._workers))

    def __len__(self):
        return len(self._workers)

    def append(self, item):
        self._workers.append(item)

    def remove(self, item):
        self._workers.remove(item)

    def __getitem__(self, sliced):
        return self._workers[sliced]

    def __setitem__(self, sliced, value):
        self._workers[sliced] = value



# from support.threads import WorkerGroup
class WorkerGroupThreadListWrapper(WorkerGroup):
    """ Tries to provide a workergroup interface to a list of ordinary thread
        objects that are not WorkerThread class
    """
    def __init__(self, threads, name="workers"):
        WorkerGroup.__init__(self, workers=threads, name=name)
        # self.workers =

    def worker_status(self, i):
        worker = self._workers[i]
        if hasattr(worker, "status"):
            return worker.status
        elif worker.isAlive():
            return "running"
        # elif hasattr(worker, "status") and worker.status=="fail":
        #     return "fail"
        # elif hasattr(worker, "status") and worker.status=="success":
        #     return "success"
        else:
            return None

    @property
    def status(self):
        return [self.worker_status(i) for i in range(self.n_workers)]

    @property
    def overall_status(self):
        # return [getattr(worker, "status", None) for worker in self._workers]
        if self.is_running:
            return "running"
        elif self.all_failures:
            return "fail"
        elif self.all_finished:
            return "success"
        else:
            return None

    @property
    def is_running(self):
        return any([worker.is_alive() for worker in self._workers])

    @property
    def all_finished(self):
        assert False, "all_finished not implemented"
        # return any([worker.is_alive() for worker in self._workers])

    @property
    def has_failures(self):
        # TODO: look for status property in thread
        assert False, "has_failures not implemented"

    def start(self):
        logger.warning("start() function in ClientWorkerGroupWrapper does nothing\n         other than set each thread status property to 'running'")
        for i in range(self.n_workers):
            self._workers[i].status = "running"

    def stop(self, i=None, lock=False):
        if lock:
            logger.warning("`lock` argument in WorkerGroupThreadListWrapper is not yet operational")
        if i is None:
            for i in range(self.n_workers):
                self._workers[i]._stop = True
                self._workers[i].status = "success"
                logger.warning("`_stop_thread` signal sent to all threads")
        else:
            self._workers[i]._stop_thread = True
            self._workers[i].status = "success"
            logger.warning("`_stop_thread` signal sent to thread {}".format(self._workers[i].name))
