import datetime
import dateutil
import dateutil.tz


# ##############################################################################
#                                    TIME
# ##############################################################################
def gettz(tz):
    """ Return a timezone object to be used by dateutul given a timezone as a
        string such as "UTC" or "Australia/Melbourne" """
    return dateutil.tz.gettz(tz)

def datetime2str(dt, format="%Y-%m-%d %H:%M:%S", tz="Australia/Melbourne"):
    """ """
    # Set timezone information
    tzinfo = dateutil.tz.gettz(tz)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tzinfo)
    else:
        dt = dt.astimezone(tzinfo)
    # format as string
    return dt.strftime(format)

# TODO: check that timestamp2str is returning time in desired timezone correctly
def timestamp2str(t, tz="Australia/Melbourne", format="%Y-%m-%d %H:%M:%S.%f %Z"):
    tzinfo = dateutil.tz.gettz(tz)
    assert tzinfo is not None, "Could not get timezone data"
    return datetime.datetime.fromtimestamp(t, tz=tzinfo).strftime(format)

def str2datetime(t, format="%Y-%m-%d %H:%M:%S", tz="Australia/Melbourne"):
    tzinfo = dateutil.tz.gettz(tz)
    assert tzinfo is not None, "Could not get timezone data"
    dt = datetime.datetime.strptime(t, format).replace(tzinfo=tzinfo)
    return dt

def str2timestamp(t, format="%Y-%m-%d %H:%M:%S", tz="Australia/Melbourne", asint=True):
    """ if asint is true, then it forces the returned value to be an integer """
    tzinfo = dateutil.tz.gettz(tz)
    assert tzinfo is not None, "Could not get timezone data"
    dt = datetime.datetime.strptime(t, format).replace(tzinfo=tzinfo)
    ts = dt.timestamp()
    if asint:
        ts = int(ts)
    return ts

def now_datetime(tz="Australia/Melbourne"):
    tzinfo = dateutil.tz.gettz(tz)
    assert tzinfo is not None, "Could not get timezone data"
    return datetime.datetime.now(tz=tzinfo)

def now_timestamp():
    tzinfo = dateutil.tz.gettz("UTC")
    assert tzinfo is not None, "Could not get timezone data"
    return datetime.datetime.now(tz=tzinfo).timestamp()

def now_string(format="%Y-%m-%dT%H:%M:%S", tz="Australia/Melbourne"):
    tzinfo = dateutil.tz.gettz(tz)
    assert tzinfo is not None, "Could not get timezone data"
    return datetime.datetime.now(tz=tzinfo).strftime(format)

def set_timezone(dt, tz="UTC"):
    """ overwrites the timezone information of a datetime and returns a copy """
    tzinfo = dateutil.tz.gettz(tz)
    return dt.replace(tzinfo=tzinfo)

def convert_timezone(dt, tz, tzin=None):
    """ Returns a copy of a datetime objet with time converted to new timezoneself.
        WARNING: it might be problematic to use tz="local" for output timezone.
        It is better to explicitly specify an actual output timezone.
    """
    # Ensure datetime object is timesone aware
    if dt.tzinfo is None:
        assert isinstance(tzin, str), \
            "\n    datetime object must either be timezone aware, OR, you should"\
            "\n    provide original timezone as a string in the `tzin` argument"
        tzinfo_in = dateutil.tz.tzlocal() if (tzin=="local") else dateutil.tz.gettz(tzin)
        dt = dt.replace(tzinfo=tzinfo_in)

    # Convert to new timesone
    tzinfo_out = dateutil.tz.tzlocal() if (tz=="local") else dateutil.tz.gettz(tz)
    return dt.astimezone(tzinfo_out)

def seconds2hms(t):
    """ Given a time in seconds, returns a string formatted as "HH:MM:SS" """
    t = int(t)
    H, r = divmod(t, 3600)
    M, S = divmod(r, 60)
    return "{:02n}:{:02n}:{:02n}".format(H,M,S)



# ##############################################################################
#                                    TIME ALIASES
# ##############################################################################
timenow_str = now_string
timenow = now_datetime
