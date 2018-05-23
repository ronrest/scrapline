from support.misc import MapDict
from support.misc import set_timezone, convert_timezone, datetime2str
from support.misc import now_datetime
from support.telegram import id_from_peerobject
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

class ProtoMessage(object):
    def __init__(self):
        self._contents = {}
        self.date_format = DATE_FORMAT
        self.tz = "UTC"

    def summary(self, format="", text_limit=20):
        return format.format(text_short=self._contents["text"][:text_limit], **self._contents)
    @property
    def dict(self):
        return self._contents
    def asdict(self):
        return self._contents
    def __str__(self):
        return self.summary()
    def __repr__(self):
        return "<MESSAGE OBJECT:  {}>".format(self.summary())
