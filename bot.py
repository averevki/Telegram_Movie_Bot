"""Bot module"""

import os
import logging
from logging import config

import requests
from telegram.ext import Updater, CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from dotenv import load_dotenv      # load variables from local environment
load_dotenv()

BOT_API = os.getenv("BOT_API")
OMDB = "http://www.omdbapi.com"
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

    def start(self, update: Update, context: CallbackContext) -> None:
        """Message that prints for new users"""
        self.logger.info("/start called")
        update.message.reply_text("Hello, I'm MovieBot :) -> /help")

    def help_text(self, update: Update, context: CallbackContext) -> None:
        """/help message"""
        self.logger.info("/help called")
        update.message.reply_text("Help will be there")  # TODO

    def any_text(self, update: Update, context: CallbackContext) -> None:
        """Bot response on not coded text"""
        self.logger.info(f"unknown command called ({update.message.text})")
        update.message.reply_text(f"Unknown command: {update.message.text}")

    def error(self, update: Update, context: CallbackContext) -> None:
        """Logs errors"""
        self.logger.exception(f"error: {context.error} - "
                              f"['{update['message']['chat']['first_name']}': '{update['message']['text']}']")
        update.message.reply_text("Sorry, this movie/show is unknown to me")

    @staticmethod
    def empty_memory(update: Update):
        update.message.reply_text("My memory is empty😕.\nLook something up! -> /find")

    def find_title(self, update: Update, context: CallbackContext) -> None:
        """/find command

        Finds movie by specifications
        """
        self.logger.info("/find called")
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
        response = requests.get(OMDB, params=params)
        movie_data = self.memory = response.json()                                  # Save found title in memory
        data_str = f"Title:    {movie_data['Title']} ({movie_data['Year']})\n" \
                   f"Genre:    {movie_data['Genre']}\n" \
                   f"Rating:    {movie_data['imdbRating']}/10\n" \
                   f"Runtime:    {movie_data['Runtime']}\n" \
                   f"Actors:    {movie_data['Actors']}\n" \
                   f"Director:    {movie_data['Director']}\n"

        poster = requests.get(movie_data["Poster"]).content
        context.bot.sendMediaGroup(chat_id=update.effective_chat.id,
                                   media=[InputMediaPhoto(poster)])  # Show poster

        buttons = [[InlineKeyboardButton("plot", callback_data=f"{self.memory['Title']} plot")],
                   [InlineKeyboardButton("trailer", callback_data=f"{self.memory['Title']} trailer")],
                   [InlineKeyboardButton("awards", callback_data=f"{self.memory['Title']} awards")],
                   [InlineKeyboardButton("rating", callback_data=f"{self.memory['Title']} rating")]]
        update.message.reply_text(data_str, reply_markup=InlineKeyboardMarkup(buttons))

    @property
    def fetch_rating(self) -> str:
        rating_str: str = ""
        for rating in self.memory["Ratings"]:
            rating_str += f"{rating['Source']}: {rating['Value']}\n"
        return f"{self.memory['Title']} ratings:\n{rating_str}"

    def rating(self, update: Update, context: CallbackContext) -> None:
        """Print out rating of the movie in memory"""
        self.logger.info("/rating called")
        if self.memory:
            update.message.reply_text(self.fetch_rating)
        else:
            self.empty_memory(update)

    @property
    def get_rated(self) -> str:
        return f"{self.memory['Title']} rated:\n{self.memory['Rated']}"

    def rated(self, update: Update, context: CallbackContext) -> None:
        """Print out rating of the movie in memory"""
        self.logger.info("/rated called")
        if self.memory:
            update.message.reply_text(self.get_rated)
        else:
            self.empty_memory(update)

    @property
    def get_plot(self) -> str:
        return f"{self.memory['Title']} plot:\n{self.memory['Plot']}"

    def plot(self, update: Update, context: CallbackContext) -> None:
        """Print out plot of the movie in memory"""
        self.logger.info("/plot called")
        if self.memory:
            update.message.reply_text(self.get_plot)
        else:
            self.empty_memory(update)

    @property
    def get_languages(self) -> str:
        return f"{self.memory['Title']} languages:\n{self.memory['Language']}"

    def language(self, update: Update, context: CallbackContext) -> None:
        """Print out available languages of the movie in memory"""
        self.logger.info("/language called")
        if self.memory:
            update.message.reply_text(self.get_languages)
        else:
            self.empty_memory(update)

    @property
    def get_awards(self) -> str:
        return f"{self.memory['Title']} awards:\n{self.memory['Awards']}"

    def awards(self, update: Update, context: CallbackContext) -> None:
        """Print out awards of the movie in memory"""
        self.logger.info("/awards called")
        if self.memory:
            update.message.reply_text(self.get_awards)
        else:
            self.empty_memory(update)

    def query_handler(self, update: Update, context: CallbackContext) -> None:
        query = update.callback_query.data
        update.callback_query.answer()
        self.logger.info(query)
        if f"{self.memory['Title']} awards" in query:
            update.callback_query.message.reply_text(self.get_awards)
        elif f"{self.memory['Title']} trailer" in query:
            pass
            # update.callback_query.message.reply_text(f"{self.memory['Title']} shit:\n{self.memory['Awards']}")
        elif f"{self.memory['Title']} rating" in query:
            update.callback_query.message.reply_text(self.fetch_rating)
        elif f"{self.memory['Title']} plot" in query:
            update.callback_query.message.reply_text(f"{self.memory['Title']} plot:\n{self.memory['Plot']}")
