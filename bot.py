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
        logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
        logging.info("Starting Bot...")

        self.updater = Updater(BOT_API, use_context=True)
        self.dp = self.updater.dispatcher

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
        logging.error(f"Update: error: {context.error}, caused by: {update}")

    def find_title(self, update, context):
        """/find command, finds movie by specifications"""
        # check arguments for year specification
        if "y=" in context.args[-1]:
            movie_name = " ".join(context.args[:-1])
            params = {
                "apikey": API_KEY,
                "t": movie_name,
                "y": context.args[-1][2:]
            }
        else:
            movie_name = " ".join(context.args)
            params = {
                "apikey": API_KEY,
                "t": movie_name,
            }

        response = requests.get("http://www.omdbapi.com", params=params)
        response.raise_for_status()
        global memory
        movie_data = memory = response.json()
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
        if memory:
            update.message.reply_text(f"{memory['Title']} rated: {memory['Rated']}")
        else:
            update.message.reply_text("My memory is empty😕")

    def language(self, update, context):
        """Print out rating of the movie in memory"""
        if memory:
            update.message.reply_text(f"{memory['Title']} languages: {memory['Language']}")
        else:
            update.message.reply_text("My memory is empty😕")

    def awards(self, update, context):
        """Print out rating of the movie in memory"""
        if memory:
            update.message.reply_text(f"{memory['Title']} awards: {memory['Awards']}")
        else:
            update.message.reply_text("My memory is empty😕")

