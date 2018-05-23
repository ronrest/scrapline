from support.misc import MapDict
from support.misc import set_timezone, convert_timezone, datetime2str
from support.misc import now_datetime
from support.telegram import id_from_peerobject
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

class ProtoMessage(object):
    def __init__(self):
        self._contents = {}

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


class TelegramMessage(ProtoMessage):
    def __init__(self, message, time_collected=None, date_format=DATE_FORMAT):
        ProtoMessage.__init__(self)
        self.date_format = date_format
        if time_collected is None:
            time_collected = now_datetime(tz="UTC")

        # convert to dict version
        if not isinstance(message, dict):
            message = message.to_dict()

        # MAP FIELDS FORM INPUT MESSAGE
        dict_mapper = MapDict()
        dict_mapper.add("id", "message_id")
        dict_mapper.add("date", "time", lambda x: datetime2str(x, format=self.date_format, tz="UTC"))
        dict_mapper.add("message", "text")
        dict_mapper.add("from_id", "author_id")
        dict_mapper.add("to_id", "group_id", lambda x: id_from_peerobject(x))
        self._contents = dict_mapper.map(message)

        # ADITIONAL FIELDS TO GET
        self._contents["id"] = "{group_id}_{message_id}".format(**self._contents)
        self._contents["time_collected"] = datetime2str(time_collected, format=self.date_format, tz="UTC")

    def summary(self, format="[{time}] ID: {id} MESSAGE: {text_short}", text_limit=20):
        return format.format(text_short=self._contents["text"][:text_limit], **self._contents)
