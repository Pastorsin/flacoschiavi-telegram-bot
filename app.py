#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import logging
import datetime
from modules.utils import *
from urllib.parse import unquote
from telegram import MessageEntity
from telegram.ext import RegexHandler
from configparser import ConfigParser
from modules.scores import ScoresManagment
from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters


class ArielTimer():

    def __init__(self, job_queue):
        self.add_jobs(job_queue)

    def add_jobs(self, job_queue):
        job_queue.run_daily(self.ariel_callback, datetime.datetime.today())

    def tomorrow_day(self):
        """Return the week day of tomorrow day."""
        return (datetime.datetime.today() + datetime.timedelta(1)).weekday()

    def random_time(self):
        """Return a Time object with random hour and minute."""
        hour = str(random.randint(0, 23))
        minute = str(random.randint(0, 59))
        return datetime.datetime.strptime(hour + ':' + minute, '%H:%M').time()

    def ariel_callback(self, bot, job):
        """Arieeeel timer."""
        bot.send_message(chat_id='445457581',
                         text=('Ari' + ('e' * random.randint(8, 25) + 'l')))
        # Remove actual job from job queue
        job.schedule_removal()
        # Add new callback for tomorrow with a random hour
        job.job_queue.run_daily(self.ariel_callback,
                                self.random_time(), (self.tomorrow_day(), ))


class CommandsManagment():

    def __init__(self, dispatcher):
        self.add_handlers(dispatcher)

    def add_handlers(self, dp):
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("search", self.search))
        dp.add_handler(CommandHandler("video", self.video))

    def start(self, bot, update):
        """Send a message when the command /start is issued."""
        update.message.reply_text('Hola amigoncho')

    def search(self, bot, update):
        """Send the first result of the Google search"""
        ns = "+".join(update.message.text.split()[1:])
        update.message.reply_text(
            unquote("https://www.google.com/search?q=" + ns + "&btnI"))

    def video(self, bot, update):
        """Send the result list of Youtube"""
        ns = "+".join(update.message.text.split()[1:])
        update.message.reply_text(
            unquote("https://www.youtube.com/search?q=" + ns))


class MessagesManagment():

    def __init__(self, dispatcher):
        self.PORN = ("petardas", "pornhub", "serviporno", "xvideos", "redtube")
        self.xd = 0
        self.add_handlers(dispatcher)

    def add_handlers(self, dp):
        regex = Utils().to_regex
        dp.add_handler(MessageHandler(Filters.voice, self.voice_reply))
        dp.add_handler(RegexHandler(regex('xd'), self.xd_reply))
        dp.add_handler(RegexHandler(regex('amigos'), self.amigos_reply))
        dp.add_handler(RegexHandler(regex('quien'), self.quien_reply))
        dp.add_handler(RegexHandler(regex('pocho'), self.pocho_reply))
        dp.add_handler(RegexHandler(regex('porno'), self.porno_reply))
        dp.add_handler(RegexHandler(regex('gracias'), self.gracias_reply))

    def voice_reply(self, bot, update):
        if update.message.voice.duration > 30:
            update.message.reply_text('Resumime el audio papá')

    def xd_reply(self, bot, update):
        self.xd += 1
        msg = 'Me dijeron {0} veces XD.'.format(self.xd)
        bot.sendMessage(update.message.chat.id, text=msg)

    def amigos_reply(self, bot, update):
        update.message.reply_text('Vos no tenés amigos pelotudo.')

    def quien_reply(self, bot, update):
        update.message.reply_text('Tu vieja.')

    def pocho_reply(self, bot, update):
        update.message.reply_text('PochoOoOOOoOoOoOOoOoo')

    def porno_reply(self, bot, update):
        msg = 'http://www.{0}.com/'.format(random.choice(self.PORN))
        update.message.reply_text(msg)

    def gracias_reply(self, bot, update):
        update.message.reply_text('De nada campeón.')


class Bot():

    def __init__(self):
        self.init_updater()
        self.set_loggin()
        self.add_jobs()
        self.add_handlers()

    def init_updater(self):
        self.updater = Updater(os.get)

    def set_loggin(self):
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        logger = logging.getLogger(__name__)

    def add_jobs(self):
        ArielTimer(self.updater.job_queue)

    def add_handlers(self):
        dp = self.updater.dispatcher
        CommandsManagment(dp)
        MessagesManagment(dp)
        ScoresManagment(dp, self.updater)

    def start(self):
        self.updater.start_polling()


if __name__ == '__main__':
    Bot().start()
