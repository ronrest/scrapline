import logging
import os
import json

import telegram
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters

from . proto_client import Proto_Client

# from datetime import datetime
logger = logging.getLogger('scraper_pipeline.clients')

class TelegramBotClient(Proto_Client):
    """
    Args:
        credentials:  (str) path to json file with credentials
    """
    def __init__(self, credentials):
        self.credentials = self.parse_credentials(credentials)

    @property
    def is_connected(self):
        assert False, "TODO: `is_connected` not implemented yet"

    def parse_credentials(self, credentials=None):
        """ If credentials is already a dictionary, then it returns it
            unmodified, otherwise if credentials is a path to a json file,
            then load as a dict
        """
        if credentials is None:
            credentials = self.credentials
        if isinstance(credentials, str):
            logger.debug("- opening credentials file: {}".format(credentials))
            with open(credentials, mode="r") as fileobj:
                parsed_credentials = json.load(fileobj)
        elif not isinstance(credentials, dict):
            raise ValueError("credentials must be a dictionary, or filepath to a valid json file")
        return parsed_credentials

    def connect(self):
        self.bot = telegram.Bot(**self.credentials)

    def disconnect(self):
        assert False, "'disconnect()' is not implemented yet"

    def reconnect(self):
        assert False, "'reconnect()' is not implemented yet"

    def ping(self):
        assert False, "'ping()' is not implemented yet"

    def send_message(self, to, text):
        self.bot.send_message(
            chat_id=to,
            text=text)

# TODO: Add function to to messages in the client, using the following code as a base
# from telegram.ext import MessageHandler, Filters
# import telegram
# from telegram.ext import Updater
# import logging
#
# # First, you have to create an Updater object.
# updater = Updater(**bot_client.credentials)
# # get access to the dispatcher
# dispatcher = updater.dispatcher
#
# def process_text_message(bot, update):
#     in_message = update.message.text # the message that was received
#     # chat = update.message.chat
#     # out_message = "Go away! you smell! {}".format(chat.id)
#     out_message = "The CHAT ID for this chat group is: {}".format(update.message.chat_id)
#     bot.send_message(
#         chat_id=update.message.chat_id,
#         text=out_message)
#
#
# text_message_handler = MessageHandler(Filters.text, process_text_message)
# dispatcher.add_handler(text_message_handler)
# updater.start_polling()
