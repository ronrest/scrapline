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

