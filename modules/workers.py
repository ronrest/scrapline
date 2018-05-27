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



