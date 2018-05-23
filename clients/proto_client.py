import logging
import os
import json

# from datetime import datetime
logger = logging.getLogger('scraper_pipeline.clients')

class Proto_Client(object):
    """
    Args:
        credentials:  (str) path to json file with credentials
    """
    def __init__(self, credentials):
        self.credentials = credentials

    @property
    def is_connected(self):
        assert False, "TODO: `is_connected` not implemented yet"

    def parse_credentials(self, credentials):
        """ If credentials is already a dictionary, then it returns it
            unmodified, otherwise if credentials is a path to a json file,
            then load as a dict
        """
        if isinstance(credentials, str):
            logger.debug("- opening credentials file: {}".format(credentials))
            with open(credentials, mode="r") as fileobj:
                parsed_credentials = json.load(fileobj)
        elif not isinstance(credentials, dict):
            raise ValueError("credentials must be a dictionary, or filepath to a valid json file")
        return parsed_credentials

    def connect(self):
        assert False, "'connect()' is not implemented yet"

    def disconnect(self):
        assert False, "'disconnect()' is not implemented yet"

    def reconnect(self):
        assert False, "'reconnect()' is not implemented yet"

    def ping(self):
        assert False, "'ping()' is not implemented yet"
