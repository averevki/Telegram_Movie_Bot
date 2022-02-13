#!/usr/bin/env python3

# Aleksandr Verevkin
# Telegram movie/show information bot
# By using omdb & imdb APIs
from telegram.ext import CommandHandler, MessageHandler, Filters
import logging
from bot import Bot

if __name__ == "__main__":
    # Bot initialization
    bot = Bot()
    # Commands
    bot.dp.add_handler(CommandHandler("start", bot.start))
    bot.dp.add_handler(CommandHandler("help", bot.help_text))
    # Movie commands
    bot.dp.add_handler(CommandHandler("find", bot.find_title))
    bot.dp.add_handler(CommandHandler("rated", bot.rated))
    bot.dp.add_handler(CommandHandler("language", bot.language))
    bot.dp.add_handler(CommandHandler("awards", bot.awards))
    # Messages
    bot.dp.add_handler(MessageHandler(Filters.text, bot.any_text))
    # Error
    bot.dp.add_error_handler(bot.error)

    # Start idling for messages
    bot.updater.start_polling()
    bot.updater.idle()

    logging.info("Bot terminated.")
