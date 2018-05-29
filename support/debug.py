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

id2sig = {sig.value:sig.name for sig in list(signal.Signals)}
sigmap = {sig.name:sig for sig in signal.Signals}

logging_level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
        }


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

# def unexpected_termination_procedure(msg, health_file="health.log", log_tz="Australia/Melbourne"):
#     error_msg = pretty_error_str(msg)
#     logger.critical(error_msg)
#     # Update health file
#     full_msg = "NO HEALTH INFORMATION\n"
#     full_msg += "PROGRAM CRASHED UNEXPECTEDLY\n"
#     full_msg += timenow_str(format="%Y-%m-%d %H:%M:%S %Z", tz=log_tz)
#     full_msg += "\n\n"+ error_msg
#     str2file(full_msg, f=health_file, mode="w")
#     raise

def configure_logging(logger_level="info", logger_name="myscraper", file=None, library_levels={}, date_format="%Y-%m-%d %H:%M:%S", log_tz="Australia/Melbourne"):
    # TODO: use key value mappings to map log level for different libraries.
    #       Currenlty hardcoding telergam as the only external library
    #  TODO: Take argument for name of current library.
    #        currently hardcodes it as "myscraper"
    logging.basicConfig(format='%(levelname)-8s %(asctime)s [%(name)s][%(threadName)s]:\n         %(message)s',
                        level=logging.WARNING,
                        filename=file,
                        datefmt=date_format
                        )
    # Set the timezone of the logging datetime stamp
    logging.Formatter.converter = lambda *args: datetime.now(tz=dateutil.tz.gettz(log_tz)).timetuple()

    for library, level in library_levels.items():
        logging.getLogger(library).setLevel(level=logging_level_map[level])
    # logging.getLogger('scraper_pipeline').setLevel(level=logging_level_map[telegram_log_level]) # telegram logs
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_level_map.get(logger_level.lower()))
    return logger

def sig_handler(sig_id=None, frame=None):
    print("OHHH SHIT! GOT A SYSTEM SIGNAL {}".format(sig_id))
    sys.exit(sig_id)

def handle_sys_signals(sigs):
    for sig in sigs:
        signal.signal(sigmap[sig], sig_handler)
