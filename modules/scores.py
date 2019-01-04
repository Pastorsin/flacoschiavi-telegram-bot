#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import datetime
from modules.utils import *
from telegram import MessageEntity
from modules.members import MembersCollection
from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters

MIN = -25
MAX = 51


class Mention():
    """docstring for ClassName"""

    def __init__(self, dispatcher, update):
        self.votes = []
        self.MAX_VOTES = 10
        self.add_handlers(dispatcher)
        self.add_jobs(update.job_queue)

    def add_handlers(self, dispatcher):
        dispatcher.add_handler(MessageHandler(
            (Filters.entity(self.mention_type)), self.reply))

    def add_jobs(self, job_queue):
        time = datetime.datetime.strptime('00:00', '%H:%M').time()
        job_queue.run_daily(self.reset_votes, time)

    def first_word(self, mentions):
        """Return the mention if it is the first word of message."""
        return next(filter((lambda mention: mention.offset == 0), mentions))

    def valid_score(self, username, message):
        """Returns a score if it is valid."""
        message = message.split()
        message.remove(username)
        if message:
            sign = message[0][0]
            score = message[0][1:]
            return message[0] if ((sign in '+-') & score.isdigit()) else ''

    def get_score_data(self):
        """Return score json."""
        with open(os.path.join('data', 'scores.json'), 'r') as scores:
            return json.load(scores)

    def save_score(self, group_key, user_key, score_value):
        """Save scores data in JSON"""
        scores_json = self.get_score_data()
        with open(os.path.join('data', 'scores.json'), 'w') as scores:
            if (group_key in scores_json) and (user_key in scores_json[group_key]):
                scores_json[group_key][user_key] += score_value
            elif (group_key in scores_json):
                scores_json[group_key][user_key] = score_value
            else:
                scores_json[group_key] = {user_key: score_value}
            json.dump(scores_json, scores, ensure_ascii=False)

    def send_successful_message(self, update, user_id):
        fullname = update.message.chat.get_member(user_id).user.full_name
        votes = self.user_votes(user_id)
        msg = 'Joya!! Voto realizado a {}. Te quedan {} votos'.format(
            fullname, votes)
        return msg

    def is_between(self, score):
        return score in range(MIN, MAX)

    def is_bot(self, bot, group_key, user_key):
        return bot.getChatMember(group_key, user_key).user.is_bot

    def is_same_user(self, update, user_key):
        return update.message.from_user.id == user_key

    def reset_votes(self, bot, update):
        self.votes = []

    def add_vote(self, user_id):
        self.votes.append(user_id)

    def user_votes(self, user_id):
        return self.MAX_VOTES - self.votes.count(user_id)

    def can_vote(self, user_id):
        return self.votes.count(user_id) < self.MAX_VOTES

    def init_score(self, bot, update):
        # Filter the mention types of message entities
        mentions_entities = update.message.parse_entities([self.mention_type])
        # Detect if the first word is a mention
        mention_key = self.first_word(mentions_entities)
        if not mention_key:
            return ''
        # Detect if score is valid
        mention_text = mentions_entities[mention_key]
        score = self.valid_score(mention_text, update.message.text)
        if not score:
            return 'Puntaje inválido maquinola. @username puntaje'
        # Get user and group id for save data
        group_key = update.message.chat.id
        user_key = self.get_user_key(mention_key, mentions_entities, group_key)
        # Dont save if user is bot or himself or not member
        if not user_key:
            return 'No es miembro humano del grupo jujuj'
        same_user = self.is_same_user(update, user_key)
        if same_user:
            return 'No te podes votar a vos mismo cabeza de plumero'
        if not self.is_between(int(score)):
            return 'AAAAA FUERA DEL RANGOOO: {}, {}'.format(MIN, MAX - 1)
        if not self.can_vote(update.message.from_user.id):
            t = (datetime.datetime.strptime('00:00', '%H:%M') - datetime.timedelta(
                hours=datetime.datetime.today().hour,
                minutes=datetime.datetime.today().minute))
            h = t.hour
            m = t.minute
            return 'Te quedaste sin votos. Volvé en {}hs {}m masomeno'.format(h, m)
        # Save score in json
        self.save_score(str(group_key), str(user_key), int(score))
        # Add vote of day
        self.add_vote(update.message.from_user.id)
        # Send successful message
        return self.send_successful_message(update, user_key)

    def reply(self, bot, update):
        update.message.reply_text(self.init_score(bot, update))


class TextMention(Mention):

    def __init__(self, dispatcher, update):
        self.mention_type = MessageEntity.TEXT_MENTION
        super(TextMention, self).__init__(dispatcher, update)

    def get_user_key(self, mention, mentions_entities, group_id):
        """Returns user id"""
        return mention.user.id


class UsernameMention(Mention):

    def __init__(self, dispatcher, update):
        self.mention_type = MessageEntity.MENTION
        super(UsernameMention, self).__init__(dispatcher, update)
        self.members = MembersCollection(dispatcher)

    def get_user_key(self, mention, mentions_entities, group_id):
        """Returns user id"""
        username = mentions_entities[mention][1:]
        return self.members.get_by_username(group_id, username)


class ScoresManagment():

    def __init__(self, dispatcher, update):
        self.add_handlers(dispatcher, update)

    def add_handlers(self, dispatcher, update):
        TextMention(dispatcher, update)
        UsernameMention(dispatcher, update)
        dispatcher.add_handler(CommandHandler("puntajes", self.scores_list))
        dispatcher.add_handler(CommandHandler("help", self.help))

    def help(self, bot, update):
        """Send a message when the command /help is issued."""
        message = open(os.path.join('data', 'score_rules.txt'),
                       'r').read().format(MIN, MAX - 1)
        update.message.reply_text(message)

    def scores_list(self, bot, update):
        with open(os.path.join('data', 'scores.json'), 'r') as scores:
            scores_json = json.load(scores)
            chat_id = str(update.message.chat.id)
            if chat_id in scores_json:
                group_scores = scores_json[chat_id]
                scores_message = '╔\n'
                for user_id, user_score in group_scores.items():
                    chat = update.message.chat
                    fullname = chat.get_member(user_id).user.full_name
                    scores_message += '╟ {} : {} puntos. \n'.format(
                        fullname, str(user_score))
                scores_message += '╚ '
                update.message.reply_text(scores_message)
            else:
                self.help(bot, update)
