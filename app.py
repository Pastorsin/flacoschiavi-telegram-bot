#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import json
import random
import logging
import threading
import urllib.parse
import urllib.request
from urllib.parse import unquote
from telegram import Bot
from modules.utils import *
from telegram.ext import RegexHandler
from modules.scores import VotesManagment
from modules.scores import UsernameMention, TextMention
from modules.storage import DBStorage
from modules.subjects import SubjectsList
from modules.ingscrap import Scrap
from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters


class CommandsManagment():

    def __init__(self, updater):
        self.add_handlers(updater.dispatcher)

    def add_handlers(self, dp):
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("search", self.search))
        dp.add_handler(CommandHandler("video", self.video))
        dp.add_handler(CommandHandler("facultad", self.send_subject_info))

    def start(self, bot, update):
        """Send a message when the command /start is issued."""
        update.message.reply_text('Hola amigoncho')

    def search(self, bot, update):
        """Send the first result of the Google search"""
        ns = "+".join(update.message.text.split()[1:])
        update.message.reply_text(
            unquote("https://www.google.com/search?q=" + ns + "&btnI"))

    def getFirstYoutubeVideo(self, video_name):
        query_string = urllib.parse.urlencode({"search_query" : video_name})
        html_content = urllib.request.urlopen(
            "http://www.youtube.com/results?" + query_string)
        search_results = re.findall(
            r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
        return ("http://www.youtube.com/watch?v=" + search_results[0])

    def video(self, bot, update):
        """Send the result list of Youtube"""
        ns = "+".join(update.message.text.split()[1:])
        update.message.reply_text(
            unquote(self.getFirstYoutubeVideo(ns)))

    def send_subject_info(self, bot, update):
        subjects = ['Conceptos y Paradigmas de Lenguajes de Programación',
                    'Matemática 3',
                    'Ingeniería de Software 2',
                    'Orientación a Objetos 2']
        url = 'https://gestiondeaulas.info.unlp.edu.ar/cursadas/'
        announcements = SubjectsList(subjects, url).get_announcements()
        update.message.reply_text(announcements)


class MessagesManagment():

    def __init__(self, updater):
        self.xd = 0
        self.add_handlers(updater.dispatcher)

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
        request = urllib.request.urlopen('http://pornhub.com/random')
        update.message.reply_text(request.url)

    def gracias_reply(self, bot, update):
        update.message.reply_text('De nada campeón.')


class Bot():

    def __init__(self):
        self.STORAGE = DBStorage()
        self.init_updater()
        self.set_logging()
        self.add_handlers()

    def set_logging(self):
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        logger = logging.getLogger(__name__)

    def init_updater(self):
        self.updater = Updater(os.getenv('my_bot_key'))

    def add_handlers(self):
        CommandsManagment(self.updater)
        MessagesManagment(self.updater)
        vote = VotesManagment(self.updater)
        TextMention(self.updater, vote, self.STORAGE)
        UsernameMention(self.updater, vote, self.STORAGE)

    def start(self):
        self.updater.start_polling()

if __name__ == '__main__':
    Bot().start()
