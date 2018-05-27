import sys
import traceback
import signal
import time
import threading
# import time
from datetime import datetime
import dateutil
import dateutil.tz

import logging

logger = logging.getLogger('myscraper')
# from . threads import get_threads_health, get_thread_name
# from . misc import str2file, timenow_str, timenow
def pretty_error_str(msg="", dec=True):
    error_type = sys.exc_info()[0]
    error_object = sys.exc_info()[1]
    error_summary = str(error_object)
    traceback_str = str(traceback.format_exc())

    # If it is a system exit signal, Get the signal name string
    if error_type == SystemExit:
        sig_code = getattr(error_object, "code", None)
        if (sig_code is not None) and (isinstance(sig_code, int)):
            sig_name = id2sig[sig_code]
            error_summary += " [{}]".format(sig_name)

    dec = "\n"+("="*60)+"\n" if dec else ""
    msg = str(msg)+"\n" if msg != "" else ""
    template = "{dec}{msg}ERROR TYPE   : {et}\nERROR SUMMARY: {es}\nTRACEBACK:\n\n{tb}\n{dec}"
    return template.format(dec=dec, msg=msg, et=error_type, es=error_summary, tb=traceback_str)


def kvlines(d, keys=None):
    if keys is None:
        keys = d.keys()
    template = "{k} = {v}"
    return "\n".join([template.format(k=key, v=d[key]) for key in keys])

def thread_status_lines(thread_statuses):
    return "\n".join(["{} = {}".format(t["name"], t["status"]) for t in thread_statuses])

def configure_logging(logging_level="info", file=None, date_format="%Y-%m-%d %H:%M:%S", log_tz="Australia/Melbourne", telegram_log_level="warning"):
    # TODO: use key value mappings to map log level for different libraries.
    #       Currenlty hardcoding telergam as the only external library
    #  TODO: Take argument for name of current library.
    #        currently hardcodes it as "myscraper"
    logging_level_map = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
            }

    logging.basicConfig(format='%(levelname)-8s %(asctime)s [%(name)s][%(threadName)s]:\n         %(message)s',
                        level=logging.WARNING,
                        filename=file,
                        datefmt=date_format
                        )
    # Set the timezone of the logging datetime stamp
    logging.Formatter.converter = lambda *args: datetime.now(tz=dateutil.tz.gettz(log_tz)).timetuple()

    logging.getLogger('telethon').setLevel(level=logging_level_map[telegram_log_level]) # telegram logs
    logger = logging.getLogger('myscraper') # my scraper logs
    logger.setLevel(logging_level_map.get(logging_level.lower()))
    return logger

