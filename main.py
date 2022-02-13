#!/usr/bin/env python3

# Aleksandr Verevkin
# Telegram movie/show information bot
# By using omdb & imdb APIs
from telegram.ext import CommandHandler, MessageHandler, Filters
from bot import Bot
# TODO separate print method
# TODO separate logging file?

if __name__ == "__main__":
    bot = Bot()                              # Bot initialization
    bot.logger.info("Bot is initialized")

    bot.dp.add_handler(CommandHandler("start", bot.start))  # Commands
    bot.dp.add_handler(CommandHandler("help", bot.help_text))

    bot.dp.add_handler(CommandHandler("find", bot.find_title))  # Movie commands
    bot.dp.add_handler(CommandHandler("rated", bot.rated))
    bot.dp.add_handler(CommandHandler("language", bot.language))
    bot.dp.add_handler(CommandHandler("awards", bot.awards))

    bot.dp.add_handler(MessageHandler(Filters.text, bot.any_text))  # Any other message

    bot.dp.add_error_handler(bot.error)  # Error

    bot.updater.start_polling()  # Start idling for messages
    bot.updater.idle()

    bot.logger.info("Bot terminated.")
