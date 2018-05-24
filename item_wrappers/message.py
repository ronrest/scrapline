DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# TODO: consider replacing this with protoItem
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
