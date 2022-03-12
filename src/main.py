#!/usr/bin/env python3

"""Telegram movie/show information bot

By using omdb & imdb APIs

Bot collecting available commands from users and
find information about movies on their foundation.
You can start with /help command.
"""

__author__ = "Aleksandr Verevkin"
__license__ = "GNU GPL v.3"
__maintainer__ = "Aleksandr Verevkin"
__status__ = "Maintenance"

from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from bot import Bot


def main():
    # Bot initialization
    bot = Bot()
    bot.logger.info("Bot is initialized and maintained")
    # Commands handlers
    bot.dp.add_handler(CommandHandler("start", bot.start))
    bot.dp.add_handler(CommandHandler("help", bot.help_text))
    # Movie commands
    bot.dp.add_handler(CommandHandler("find", bot.find_title))
    bot.dp.add_handler(CommandHandler("rate", bot.rated))
    bot.dp.add_handler(CommandHandler("rated", bot.rated))
    bot.dp.add_handler(CommandHandler("language", bot.language))
    bot.dp.add_handler(CommandHandler("languages", bot.language))
    bot.dp.add_handler(CommandHandler("award", bot.awards))
    bot.dp.add_handler(CommandHandler("awards", bot.awards))
    bot.dp.add_handler(CommandHandler("plot", bot.plot))
    bot.dp.add_handler(CommandHandler("rating", bot.rating))
    bot.dp.add_handler(CommandHandler("ratings", bot.rating))
    bot.dp.add_handler(CommandHandler("link", bot.link))
    # Any other message
    bot.dp.add_handler(MessageHandler(Filters.text, bot.any_text))
    # Query handler
    bot.dp.add_handler(CallbackQueryHandler(bot.query_handler))
    # Error
    bot.dp.add_error_handler(bot.error)
    # Start idling for messages
    bot.updater.start_polling()
    bot.updater.idle()

    bot.logger.info("Bot terminated.")


if __name__ == "__main__":
    main()
