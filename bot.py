"""Bot module"""

import requests
import os
from telegram.ext import *
from telegram import *
import logging
from logging import config

from dotenv import load_dotenv      # load variables from local environment
load_dotenv()
BOT_API = os.getenv("BOT_API")
OMDB_API = os.getenv("OMDB_API")
IMDB_API = os.getenv("IMDB_API")


class Bot:
    def __init__(self) -> None:
        """Initialize bot and his logger"""
        self.updater = Updater(BOT_API, use_context=True)  # Set up bot updater and dispatcher
        self.dp = self.updater.dispatcher

        logging.config.fileConfig("logging.conf")  # Use logger config
        self.logger = logging.getLogger(__name__)  # Create logger

        self.memory: dict = {}  # last title that user found, stored in memory

    @staticmethod
    def start(update: Update, context: CallbackContext) -> None:
        """Message that prints for new users"""
        update.message.reply_text("Hello, I'm MovieBot :) -> /help")

    @staticmethod
    def help_text(update: Update, context: CallbackContext) -> None:
        """/help message"""
        update.message.reply_text("Help will be there")  # TODO

    @staticmethod
    def any_text(update: Update, context: CallbackContext) -> None:
        """Bot response on not coded text"""
        update.message.reply_text(f"Unknown command: {update.message.text}")

    def error(self, update: Update, context: CallbackContext) -> None:
        """Logs errors"""
        update.message.reply_text("Sorry, this movie/show is unknown to me")
        self.logger.exception(f"error: {context.error} - "
                              f"['{update['message']['chat']['first_name']}': '{update['message']['text']}']")

    def find_title(self, update: Update, context: CallbackContext) -> None:
        """/find command, finds movie by specifications"""
        if "y=" in context.args[-1]:                    # check arguments for year specification
            movie_name = " ".join(context.args[:-1])
            params = {
                "apikey": OMDB_API,
                "t": movie_name,
                "y": context.args[-1][2:]
            }
        else:
            movie_name = " ".join(context.args)
            params = {
                "apikey": OMDB_API,
                "t": movie_name,
            }
        response = requests.get("http://www.omdbapi.com", params=params)
        response.raise_for_status()
        movie_data = self.memory = response.json()                                  # Save found title in memory
        data_str = f"Title:    {movie_data['Title']} ({movie_data['Year']})\n" \
                   f"Genre:    {movie_data['Genre']}\n" \
                   f"Rating:    {movie_data['imdbRating']}/10\n" \
                   f"Runtime:    {movie_data['Runtime']}\n" \
                   f"Actors:    {movie_data['Actors']}\n" \
                   f"Director:    {movie_data['Director']}\n"

        poster = requests.get(movie_data["Poster"]).content
        context.bot.sendMediaGroup(chat_id=update.effective_chat.id, media=[InputMediaPhoto(poster)])  # Show poster
        buttons = [[InlineKeyboardButton("awards", callback_data=f"{self.memory['Title']} awards")],
                   [InlineKeyboardButton("trailer", callback_data=f"{self.memory['Title']} trailer")]]
        update.message.reply_text(data_str, reply_markup=InlineKeyboardMarkup(buttons))

    def rated(self, update: Update, context: CallbackContext) -> None:
        """Print out rating of the movie in memory"""
        if self.memory:
            update.message.reply_text(f"{self.memory['Title']} rated:\n{self.memory['Rated']}")
        else:
            update.message.reply_text("My memory is empty😕.\nLook something up! -> /find")

    def language(self, update: Update, context: CallbackContext) -> None:
        """Print out rating of the movie in memory"""
        if self.memory:
            update.message.reply_text(f"{self.memory['Title']} languages:\n{self.memory['Language']}")
        else:
            update.message.reply_text("My memory is empty😕.\nLook something up! -> /find")

    def awards(self, update: Update, context: CallbackContext) -> None:
        """Print out rating of the movie in memory"""
        if self.memory:
            update.message.reply_text(f"{self.memory['Title']} awards:\n{self.memory['Awards']}")
        else:
            update.message.reply_text("My memory is empty😕.\nLook something up! -> /find")

    def query_handler(self, update: Update, context: CallbackContext) -> None:
        query = update.callback_query.data
        update.callback_query.answer()
        self.logger.info(query)
        if f"{self.memory['Title']} awards" in query:
            update.callback_query.message.reply_text(f"{self.memory['Title']} awards:\n{self.memory['Awards']}")

