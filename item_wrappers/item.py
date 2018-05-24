DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

class ProtoItem(object):
    def __init__(self):
        self._contents = {}
        self.date_format = DATE_FORMAT
        self.tz = "UTC"

    def summary(self, format="", text_limit=20):
        return format.format(**self._contents)
    @property
    def dict(self):
        return self._contents
    def asdict(self):
        return self._contents
    def __str__(self):
        assert False, "__str__() needs to be implemented"
        # return self.summary()
    def __repr__(self):
        return "<ITEM OBJECT:  {}>".format(self.__str__())
