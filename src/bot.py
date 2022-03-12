"""Bot module"""

from os import getenv, path
import logging
from logging import config

import requests
from telegram.ext import Updater, CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from dotenv import load_dotenv      # load variables from local environment
load_dotenv()

BOT_API = getenv("BOT_API")
OMDB = "http://www.omdbapi.com"
OMDB_API = getenv("OMDB_API")
IMDB_TRAILER_REQ = "https://imdb-api.com/en/API/YouTubeTrailer"
IMDB_API = getenv("IMDB_API")
IMDB_LINK = "https://www.imdb.com/title/"


class Bot:
    """Bot operations

    Available bot commands and operations
    API requests
    """
    HELP_MSG = "Available commands:\n" \
               "    /help\n" \
               "    /find [title] [y=year] (/find The Godfather y=1972)\n" \
               "After you find a movie, use buttons under it to get more information or " \
               "use commands to get information about last movie from bot memory:\n" \
               "    /rate|/rated -- movie PG\n" \
               "    /award|/awards -- awards and nominations\n" \
               "    /rating|/ratings -- movie ratings\n" \
               "    /language|/languages -- movie languages\n" \
               "    /plot -- short plot description\n" \
               "    /link - IMDB movie page\n"

    def __init__(self) -> None:
        """Initialize bot and his logger"""
        # Set up bot updater and dispatcher
        self.updater = Updater(BOT_API, use_context=True)
        self.dp = self.updater.dispatcher
        # Set up logger with bot config
        logging.config.fileConfig(path.join(path.dirname(path.abspath(__file__)), 'logging.conf'))
        self.logger = logging.getLogger(__name__)  # Create logger
        # Set up bot memory
        self.memory: dict = {}  # last title that user found, stored in memory

    def start(self, update: Update, context: CallbackContext) -> None:
        """Message that prints for new users"""
        self.logger.info("/start called")
        update.message.reply_text("Hello, I'm MovieBot :) -> /help")

    def help_text(self, update: Update, context: CallbackContext) -> None:
        """/help message"""
        self.logger.info("/help called")
        update.message.reply_text(self.HELP_MSG)

    def any_text(self, update: Update, context: CallbackContext) -> None:
        """Bot response on not coded text"""
        self.logger.info(f"unknown command called ({update.message.text})")
        update.message.reply_text(f"Unknown command: {update.message.text} -> /help")

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
            omdb_params = {
                "apikey": OMDB_API,
                "t": movie_name,
                "y": context.args[-1][2:]
            }
        else:
            movie_name = " ".join(context.args)
            omdb_params = {
                "apikey": OMDB_API,
                "t": movie_name,
            }
        response = requests.get(OMDB, params=omdb_params)
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

        buttons = [[InlineKeyboardButton("Plot", callback_data=f"{movie_data['Title']}:plot"),
                   InlineKeyboardButton("Trailer", url=self.get_trailer_url(movie_data["imdbID"])),
                   InlineKeyboardButton("Ratings", callback_data=f"{movie_data['Title']}:ratings")],
                   [InlineKeyboardButton("IMDB page", url=f"{IMDB_LINK}{movie_data['imdbID']}")]]
        print(self.get_plot(movie_data))
        print(self.fetch_rating(movie_data))
        update.message.reply_text(data_str, reply_markup=InlineKeyboardMarkup(buttons))

    @staticmethod
    def get_trailer_url(imdb_id: str) -> str:
        """Return movie youtube trailer url as string
        using IMDB API
        """
        imdb_params = {
            "apiKey": IMDB_API,
            "id": imdb_id
        }
        return requests.get(IMDB_TRAILER_REQ, imdb_params).json()["videoUrl"]

    @property
    def get_link(self) -> str:
        """Imdb movie link getter"""
        return f"{self.memory['Title']} on IMDB:\n{IMDB_LINK}{self.memory['imdbID']}"

    def link(self, update: Update, context: CallbackContext) -> None:
        """/link command

        Print out IMDB link of the movie in memory
        """
        self.logger.info("/link called")
        if self.memory:
            update.message.reply_text(self.get_link)
        else:
            self.empty_memory(update)

    @staticmethod
    def fetch_rating(movie_json: dict) -> str:
        """Assemble movie ratings from different websites and
        return it as string
        """
        rating_str: str = ""
        for rating in movie_json["Ratings"]:
            rating_str += f"{rating['Source']}: {rating['Value']}\n"
        return f"{movie_json['Title']} ratings:\n{rating_str}"

    def rating(self, update: Update, context: CallbackContext) -> None:
        """/rating command

        Print out rating of the movie in memory
        """
        self.logger.info("/rating called")
        if self.memory:
            update.message.reply_text(self.fetch_rating(self.memory))
        else:
            self.empty_memory(update)

    @property
    def get_rated(self) -> str:
        """Movie rate getter"""
        return f"{self.memory['Title']} rated:\n{self.memory['Rated']}"

    def rated(self, update: Update, context: CallbackContext) -> None:
        """/rated command

        Print out rating of the movie in memory
        """
        self.logger.info("/rated called")
        if self.memory:
            update.message.reply_text(self.get_rated)
        else:
            self.empty_memory(update)

    @staticmethod
    def get_plot(movie_json: dict) -> str:
        """Movie plot getter"""
        return f"{movie_json['Title']} plot:\n{movie_json['Plot']}"

    def plot(self, update: Update, context: CallbackContext) -> None:
        """/plot command

        Print out plot of the movie in memory
        """
        self.logger.info("/plot called")
        if self.memory:
            update.message.reply_text(self.get_plot(self.memory))
        else:
            self.empty_memory(update)

    @property
    def get_languages(self) -> str:
        """Movie languages getter"""
        return f"{self.memory['Title']} languages:\n{self.memory['Language']}"

    def language(self, update: Update, context: CallbackContext) -> None:
        """/language command

        Print out available languages of the movie in memory
        """
        self.logger.info("/language called")
        if self.memory:
            update.message.reply_text(self.get_languages)
        else:
            self.empty_memory(update)

    @property
    def get_awards(self) -> str:
        """Awards getter"""
        return f"{self.memory['Title']} awards:\n{self.memory['Awards']}"

    def awards(self, update: Update, context: CallbackContext) -> None:
        """/awards command

        Print out awards of the movie in memory
        """
        self.logger.info("/awards called")
        if self.memory:
            update.message.reply_text(self.get_awards)
        else:
            self.empty_memory(update)

    def query_handler(self, update: Update, context: CallbackContext) -> None:
        """Buttons handler"""
        query = update.callback_query.data
        update.callback_query.answer()
        self.logger.info(query)

        title, kword = query.split(":")
        omdb_params = {
            "apikey": OMDB_API,
            "t": title,
        }
        data = requests.get(OMDB, params=omdb_params).json()
        if kword == "ratings":
            update.callback_query.message.reply_text(self.fetch_rating(data))
        elif kword == "plot":
            update.callback_query.message.reply_text(self.get_plot(data))
