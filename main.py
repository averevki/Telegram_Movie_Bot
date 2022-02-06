#!/usr/bin/env python3

# Aleksandr Verevkin
# Telegram movie/show information bot
import requests
import os
from telegram.ext import *
from telegram import *
import logging
BOT_API = os.getenv("BOT_API", None)
API_KEY = os.getenv("API_KEY", None)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.info("Starting Bot...")

updater = Updater(BOT_API, use_context=True)
dp = updater.dispatcher


def start(update, context):
    # TODO start message
    # update.message.reply_text("Hello :) -> /help")
    exec(update.message.reply_text("Hello :) -> /help"))


def help_text(update, context):
    # TODO help message
    update.message.reply_text("Help will be there")


def error(update, context):
    """Logs errors"""
    update.message.reply_text("Sorry, this movie/show is unknown to me")
    logging.error(f"Update: {update} caused error {context.error}")


def any_text(update, context):
    update.message.reply_text(f"You said {update.message.text}")


def find_title(update, context):
    movie_name = " ".join(context.args)
    params = {
        "apikey": API_KEY,
        "t": movie_name,
    }

    response = requests.get("http://www.omdbapi.com", params=params)
    response.raise_for_status()

    movie_data = response.json()
    data_str = f"Title:    {movie_data['Title']} ({movie_data['Year']})\n" \
               f"Genre:    {movie_data['Genre']}\n" \
               f"Rating:    {movie_data['imdbRating']}/10\n" \
               f"Runtime:    {movie_data['Runtime']}\n" \
               f"Actors:    {movie_data['Actors']}\n" \
               f"Director:    {movie_data['Director']}\n"

    poster = requests.get(movie_data["Poster"]).content
    context.bot.sendMediaGroup(chat_id=update.effective_chat.id, media=[InputMediaPhoto(poster)])
    update.message.reply_text(data_str)


# Commands
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help_text))
dp.add_handler(CommandHandler("find", find_title))
# Messages
dp.add_handler(MessageHandler(Filters.text, any_text))
# Error
dp.add_error_handler(error)


# Idling for messages
updater.start_polling()
updater.idle()

logging.info("Bot terminated.")
