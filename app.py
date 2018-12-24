#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from urllib.parse import unquote
from configparser import ConfigParser
from utils import *
import os
import sys
import logging
import random
import datetime

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Data
DATA = {
    'amigos': amigos,
    'quien': quien,
    'pocho': pocho,
    'porno': porno,
    'gracias': gracias,
    'xd': xd,
    'cara de': cara_de
}


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.


def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hola amigoncho')


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Que te ayude tu vieja')


def search(bot, update):
    """Send the first result of the Google search"""
    ns = "+".join(update.message.text.split()[1:])
    update.message.reply_text(
        unquote("https://www.google.com/search?q=" + ns + "&btnI"))


def video(bot, update):
    """Send the result list of Youtube"""
    ns = "+".join(update.message.text.split()[1:])
    update.message.reply_text(
        unquote("https://www.youtube.com/search?q=" + ns))


def reply(bot, update):
    """Respond to the user."""
    message = update.message.text.lower()
    # Filter the words keys
    words = list(filter(lambda key: key in message, DATA.keys()))
    # Respond
    for w in words:
        update.message.reply_text(DATA[w]())


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def tomorrow_day():
    """Return the week day of tomorrow day."""
    return (datetime.datetime.today() + datetime.timedelta(1)).weekday()


def random_time():
    """Return a Time object with random hour and minute."""
    hour = str(random.randint(0, 23))
    minute = str(random.randint(0, 59))
    return datetime.datetime.strptime(hour + ':' + minute, '%H:%M').time()


def callback_ariel(bot, job):
    """Arieeeel timer."""
    bot.send_message(chat_id='445457581',
                     text=('Ari' + ('e' * random.randint(8, 25) + 'l')))
    # Remove actual job from job queue
    job.schedule_removal()
    # Add new callback for tomorrow with a random hour
    job.job_queue.run_daily(callback_ariel, random_time(), (tomorrow_day(), ))


def main():
    """Start the bot."""
    updater = Updater(os.getenv('my_bot_key'))

    # Create a job queue timer
    j = updater.job_queue
    j.run_daily(callback_ariel, datetime.datetime.today())

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("search", search))
    dp.add_handler(CommandHandler("video", video))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, reply))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
