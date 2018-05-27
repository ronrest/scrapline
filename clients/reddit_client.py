import praw
import threading
from . proto_client import Proto_Client, logger

class RedditClient(Proto_Client):
    def __init__(self, credentials, subreddits=None):
        """
        Args:
            credentials:    (str | dict)
                a dictionary object, or a path to json file
            subredits:      (list of str)
                list of subreddit names (without "/r/")
        """
        Proto_Client.__init__(self, credentials)
        self.credentials = self.parse_credentials()
        self.subreddits = subreddits
        self.item_lock = threading.Lock()

    def connect(self):
        logger.info("Connecting to reddit client")
        self.reddit = praw.Reddit(**self.credentials)
        self.reddit.read_only = True # Enable read only mode
        logger.debug("connected succesfully to reddit client")

    def get_item(self, timeout=None):
        # TODO: See if there is a way to do timeout on this stream generator
        if timeout is not None:
            assert False, "Timeout in reddit_client.get_item() is not implemented yet"

        with self.item_lock:
            item = next(self.comments_stream)
        return item

    def start(self):
        logger.info("Starting stream of comments from reddit")
        # subreddits = ["funny","science"]
        self.subreddit_object = self.reddit.subreddit("+".join(self.subreddits))
        self.comments_stream = self.subreddit_object.stream.comments()
