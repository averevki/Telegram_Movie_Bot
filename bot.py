import requests
import os
from telegram.ext import *
from telegram import *
import logging
BOT_API = os.getenv("BOT_API", None)
API_KEY = os.getenv("API_KEY", None)
memory: dict = {}
# TODO separate print method
# TODO separate logging file?

class Bot:
    def __init__(self):
        logging.basicConfig(format="%(asctime)s_%(name)s_%(levelname)s_%(message)s", level=logging.INFO)
        logging.info("Starting Bot...")

        self.updater = Updater(BOT_API, use_context=True)
        self.dp = self.updater.dispatcher

    def start(self, update, context):
        # TODO start message
        update.message.reply_text("Hello :) -> /help")  # TODO

    def help_text(self, update, context):
        # TODO help message
        update.message.reply_text("Help will be there")  # TODO

    def error(self, update, context):
        """Logs errors"""
        update.message.reply_text("Sorry, this movie/show is unknown to me")
        logging.error(f"Update: error: {context.error}, caused by: {update}")

