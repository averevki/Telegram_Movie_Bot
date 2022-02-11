#!/usr/bin/env python3

# Aleksandr Verevkin
# Telegram movie/show information bot
# By using omdb & imdb APIs
import requests
import os
from telegram.ext import *
from telegram import *
import logging
from bot import Bot
BOT_API = os.getenv("BOT_API", None)
API_KEY = os.getenv("API_KEY", None)
memory: dict = {}


def any_text(update, context):
    update.message.reply_text(f"You said {update.message.text}")


def find_title(update, context):
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
    print(f"HI {memory}")
    data_str = f"Title:    {movie_data['Title']} ({movie_data['Year']})\n" \
               f"Genre:    {movie_data['Genre']}\n" \
               f"Rating:    {movie_data['imdbRating']}/10\n" \
               f"Runtime:    {movie_data['Runtime']}\n" \
               f"Actors:    {movie_data['Actors']}\n" \
               f"Director:    {movie_data['Director']}\n"

    poster = requests.get(movie_data["Poster"]).content
    context.bot.sendMediaGroup(chat_id=update.effective_chat.id, media=[InputMediaPhoto(poster)])
    update.message.reply_text(data_str)


def rated(update, context):
    """Print out rating of the movie in memory"""
    if memory:
        update.message.reply_text(f"{memory['Title']} rated: {memory['Rated']}")
    else:
        update.message.reply_text("My memory is empty😕")


def language(update, context):
    """Print out rating of the movie in memory"""
    if memory:
        update.message.reply_text(f"{memory['Title']} languages: {memory['Language']}")
    else:
        update.message.reply_text("My memory is empty😕")


def awards(update, context):
    """Print out rating of the movie in memory"""
    if memory:
        update.message.reply_text(f"{memory['Title']} awards: {memory['Awards']}")
    else:
        update.message.reply_text("My memory is empty😕")


if __name__ == "__main__":
    # Bot initialization
    bot = Bot()
    # Commands
    bot.dp.add_handler(CommandHandler("start", bot.start))
    bot.dp.add_handler(CommandHandler("help", bot.help_text))
    # Movie commands
    bot.dp.add_handler(CommandHandler("find", find_title))
    bot.dp.add_handler(CommandHandler("rated", rated))
    bot.dp.add_handler(CommandHandler("language", language))
    bot.dp.add_handler(CommandHandler("awards", awards))
    # Messages
    bot.dp.add_handler(MessageHandler(Filters.text, any_text))
    # Error
    bot.dp.add_error_handler(bot.error)

    # Idling for messages
    bot.updater.start_polling()
    bot.updater.idle()

    logging.info("Bot terminated.")
