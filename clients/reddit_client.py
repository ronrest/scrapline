import praw
from . proto_client import Proto_Client, logger

class RedditClient(Proto_Client):
    def __init__(self, credentials, subredits=None):
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

    def connect(self):
        logger.info("Connecting to reddit client")
        self.reddit = praw.Reddit(**self.credentials)
        self.reddit.read_only = True # Enable read only mode
        logger.debug("connected succesfully to reddit client")

    def get_item(self):
        # Do threadlocking to get message
        # messages are in an iterator interface, which can be extracted using
        # next(x) applied to the `self.comments_stream` object
        #
        # item = next(self.comments_stream)
        assert False, "`get_item()` not implemented yet"

    def start(self):
        logger.info("Starting stream of comments from reddit")
        # subreddits = ["funny","science"]
        self.subreddit_object = client.reddit.subreddit("+".join(self.subreddits))
        self.comments_stream = subreddit_object.stream.comments()
