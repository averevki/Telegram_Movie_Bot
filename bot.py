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
    def __init__(self):
        """Initialize bot and his logger"""
        self.updater = Updater(BOT_API, use_context=True)  # Set up bot updater and dispatcher
        self.dp = self.updater.dispatcher

        logging.config.fileConfig("logging.conf")  # Use logger config
        self.logger = logging.getLogger(__name__)  # Create logger

        self.memory: dict = {}  # last title that user found, stored in memory

    def start(self, update, context):
        """Message that prints for new users"""
        update.message.reply_text("Hello :) -> /help")  # TODO

    def help_text(self, update, context):
        """/help message"""
        update.message.reply_text("Help will be there")  # TODO

    def any_text(self, update, context):
        """Bot response on not coded text"""
        update.message.reply_text(f"You said {update.message.text}")

    def error(self, update, context):
        """Logs errors"""
        update.message.reply_text("Sorry, this movie/show is unknown to me")
        self.logger.exception(f"error: {context.error} - "
                              f"['{update['message']['chat']['first_name']}': '{update['message']['text']}']")

    def find_title(self, update, context):
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
        context.bot.sendMediaGroup(chat_id=update.effective_chat.id, media=[InputMediaPhoto(poster)])
        update.message.reply_text(data_str)

    def rated(self, update, context):
        """Print out rating of the movie in memory"""
        if self.memory:
            update.message.reply_text(f"{self.memory['Title']} rated: {self.memory['Rated']}")
        else:
            update.message.reply_text("My memory is empty😕")

    def language(self, update, context):
        """Print out rating of the movie in memory"""
        if self.memory:
            update.message.reply_text(f"{self.memory['Title']} languages: {self.memory['Language']}")
        else:
            update.message.reply_text("My memory is empty😕")

    def awards(self, update, context):
        """Print out rating of the movie in memory"""
        if self.memory:
            update.message.reply_text(f"{self.memory['Title']} awards: {self.memory['Awards']}")
        else:
            update.message.reply_text("My memory is empty😕")
