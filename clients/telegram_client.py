"""
Client For connecting to telegram
"""

import logging
import json

# part of a client > process > uplaoder pipeline
import telethon
from telethon import TelegramClient as TelethonClient
from telethon import events
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.types import PeerUser, PeerChat, PeerChannel

from datetime import datetime
from support.debug import pretty_error_str
logger = logging.getLogger('myscraper.modules') # my scraper logs

QUEUE_TERMINATING_VALUE = "zzz this is a killer"

# default amount of time to wait before retry
SPAM_BACKOFF_TIME = 180 # when receive a HTTP 429 too many requests error
SERVER_DOWN_DELAY = 10  # when receive some server side error


class TelegramClient(object):
    def __init__(self, credentials, n_readers, filter=None, **kwargs):
        """
        Args:
            credentials:   (str | dict)
                either a dictionary with credentials, or a filepath to a json
                file that can be loaded as a dictionary.

        Optional Args:
            filter: (list of str | None)(default=None)
                subset of groups/chats to monitor. Set to None to monitor all
                subscribed groups
        **kwargs:
            arguments to pass to `Telethon.TelegramClient()``
        """
        self.n_readers = n_readers
        self.readers = []
        self.client = None
        self.filter = filter
        self.credentials = self.parse_credentials(credentials)
        self.kwargs = kwargs
        self.session_name = 'session_telethon_api'
        self._me = None

    @property
    def me(self):
        if self.client is None:
            self._me = None
        elif self._me is None:
            self._me = self.client.get_me().to_dict()
        return self._me

    @property
    def read_thread(self):
        return getattr(self.client, "_recv_thread", None)

    @property
    def input_q(self):
        """ Get the queue used by the client """
        updates = getattr(self.client, "updates", None)
        return getattr(updates, "_updates", None)

    @property
    def worker_threads(self):
        """ Get the list of worker threads used by the client """
        updates = getattr(self.client, "updates", None)
        return getattr(updates, "_worker_threads", "hooooli")

    @property
    def is_connected(self):
        # TODO: A more sophisicated way of telling if it is connected.
        if self.client is not None:
            return True
        else:
            return False

    def connect(self):
        """ credentials=credentials json file with 'id', 'phone' and 'hash' values """
        logger.info("CONNECTING TO TELEGRAM")
        self.client = TelethonClient(self.session_name,
                                api_id=self.credentials['id'],
                                api_hash=self.credentials['hash'],
                                update_workers=self.n_readers,
                                **self.kwargs
                                )
        self.client.start(phone=self.credentials['phone'])
        logger.debug("- connected!")

    def reconnect(self):
        pass

    def disconnect(self):
        pass

    def ping(self):
        pass

    def get_channel(self):
        pass

    def stream(self, handler_func):
        """ Stream all new messages coming in """
        self.client.add_event_handler(
            callback=handler_func,
            event=events.NewMessage(incoming=True, chats=self.filter)
            )

    def parse_credentials(self, credentials):
        """ If credentials is a path to a json file, then load as a dict """
        if isinstance(credentials, str):
            logger.debug("- opening credentials file: {}".format(credentials))
            with open(credentials, mode="r") as fileobj:
                parsed_credentials = json.load(fileobj)
        elif not isinstance(credentials, dict):
            raise ValueError("credentials must be a dictionary, or filepath to a valid json file")
        return parsed_credentials


    def list_subscribed_groups(client):
        # """ Get the set of names of the groups, and channels you are subscribed to """
        # chats = client.get_dialogs(limit=None)
        # group_names = {get_entity_name(chat.entity) for chat in chats if isinstance(chat.entity, (telethon.tl.types.Channel, telethon.tl.types.Chat))}
        # return group_names
        pass

    def get_entity_name(self, entity):
        """ Given a Telethon Entity object it returns the name of that entity """
        name = getattr(entity, "username", getattr(entity, "title", None))
        name = name if name is not None else telethon.utils.get_display_name(entity)
        return name

    def join_group(self, id):
        """ Given a group id it joins that group """
        assert isinstance(id, int), "ID must be an integer id"
        ch = self.client.get_input_entity(PeerChannel(id))
        self.client(JoinChannelRequest(ch))

    def leave_group(sef, id):
        """ Given a group id it unsubscribes that group """
        assert isinstance(id, int), "ID must be an integer id"
        ch = self.client.get_input_entity(PeerChannel(id))
        self.client(LeaveChannelRequest(ch))
