from . message import ProtoMessage
from support.datetimefuncs import now_string, timestamp2str


class RedditMessage(ProtoMessage):
    def __init__(self, message):
        ProtoMessage.__init__(self)
        self._contents = {}
        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.tz = "UTC"

    def extract_contents(self, message):
        self._contents = {
            "id": comment.id,
            "created_utc": timestamp2str(comment.created_utc, tz=self.tz, format=self.format), # TODO: convert to timestring
            # "retrieved_on": now_string(format=self.date_format, tz=self.tz),      # TODO: import library to get timenow as string
            # "author": comment.author.id,
            "body": comment.body,
            "score": comment.score,
            "ups": comment.ups,
            "downs": comment.downs,
            "gilded": comment.gilded,
            "stickied": int(comment.stickied),
            # "distinguished": comment.distinguished,
            # "controversiality": comment.controversiality,
            "parent_id": comment.parent_id,
            "is_root": comment.is_root,
            # "edited": int(comment.edited), # need to coerce to integer (sometimes False, sometimes a timestamp)
            # "archived": comment.archived,
            # "submission": comment.submission.id,
            # "subreddit": comment.subreddit.display_name,
            "scrape_status": "new",
            }


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
