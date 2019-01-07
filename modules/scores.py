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

    def get_mentions_entities(self, update):
        """Returns a dict with (mention:word)"""
        return update.message.parse_entities([self.mention_type])

    def get_mention_offset_zero(self, update):
        """Returns the mention in offset 0"""
        entities = self.get_mentions_entities(update)
        l = list(filter((lambda mention: mention.offset == 0), entities))
        return l.pop() if l else None

    def is_first_word(self, update):
        """Returns if mention is the first word of message."""
        return bool(self.get_mention_offset_zero(update))

    def get_first_word(self, update):
        """Returns the first word of mention"""
        entities = self.get_mentions_entities(update)
        return entities[self.get_mention_offset_zero(update)]

    def get_score(self, update):
        """"""
        username = self.get_first_word(update)
        message = update.message.text.split()
        message.remove(username)
        return message[0]

    def is_valid_score(self, update):
        """Returns if the mention is followed by a plus sign or minus sign and a number"""
        score = self.get_score(update)
        return (score[0] in '+-') and score[1:].isdigit()

    def is_member(self, update):
        return bool(self.get_user_id(update))

    def get_score_data(self):
        """Return score json."""
        with open(os.path.join('data', 'scores.json'), 'r') as scores:
            return json.load(scores)

    def save_score(self, update):
        """Save scores data in JSON"""
        group_key = update.message.chat.id
        user_key = self.get_user_id(update)
        score_value = int(self.get_score(update))
        scores_json = self.get_score_data()
        with open(os.path.join('data', 'scores.json'), 'w') as scores:
            if (group_key in scores_json) and (user_key in scores_json[group_key]):
                scores_json[group_key][user_key] += score_value
            elif (group_key in scores_json):
                scores_json[group_key][user_key] = score_value
            else:
                scores_json[group_key] = {user_key: score_value}
            json.dump(scores_json, scores, ensure_ascii=False)

    def send_successful_message(self, update):
        fullname = update.message.chat.get_member(
            self.get_user_id(update)).user.full_name
        votes = self.user_votes(update.message.from_user.id)
        msg = 'Joya!! Voto realizado a {}. Te quedan {} votos'.format(
            fullname, votes)
        return msg

    def is_between(self, update):
        return int(self.get_score(update)) in range(MIN, MAX)

    def is_bot(self, bot, group_key, user_key):
        return bot.getChatMember(group_key, user_key).user.is_bot

    def is_not_same_user(self, update):
        return update.message.from_user.id != self.get_user_id(update)

    def reset_votes(self, bot, update):
        self.votes = []

    def add_vote(self, user_id):
        self.votes.append(user_id)

    def user_votes(self, user_id):
        return self.MAX_VOTES - self.votes.count(user_id)

    def can_vote(self, update):
        return self.votes.count(update.message.from_user.id) < self.MAX_VOTES

    def msg_cant_vote(self):
        t = (datetime.datetime.strptime('00:00', '%H:%M') - datetime.timedelta(
            hours=datetime.datetime.today().hour,
            minutes=datetime.datetime.today().minute))
        h = t.hour
        m = t.minute
        return 'Te quedaste sin votos. Volvé en {}hs {}m masomeno'.format(h, m)

    def checks(self):
        return {
            self.is_first_word: 'Mencionaste a alguien, acordate que lo podes puntuar <.<',
            self.is_member: 'No es miembro humano del grupo jujuj',
            self.is_not_same_user: 'No te podes votar a vos mismo cabeza de plumero',
            self.is_valid_score: 'Puntaje inválido maquinola. @username puntaje',
            self.is_between: 'AAAAA FUERA DEL RANGOOO: {}, {}'.format(MIN, MAX - 1),
            self.can_vote: self.msg_cant_vote()
        }

    def get_message(self, bot, update):
        # Check before save score
        for valid_msg, msg in self.checks().items():
            if not valid_msg(update):
                return msg
        # Save score
        self.save_score(update)
        # Add vote of day
        self.add_vote(update.message.from_user.id)
        # Send successful message
        return self.send_successful_message(update)

    def reply(self, bot, update):
        update.message.reply_text(self.get_message(bot, update))


class TextMention(Mention):

    def __init__(self, dispatcher, update):
        self.mention_type = MessageEntity.TEXT_MENTION
        super(TextMention, self).__init__(dispatcher, update)

    def get_user_id(self, update):
        """Returns user id"""
        return self.get_mention_offset_zero(update).user.id


class UsernameMention(Mention):

    def __init__(self, dispatcher, update):
        self.mention_type = MessageEntity.MENTION
        super(UsernameMention, self).__init__(dispatcher, update)
        self.members = MembersCollection(dispatcher)

    def get_user_id(self, update):
        """Returns user id"""
        username = self.get_first_word(update)[1:]
        group_id = update.message.chat.id
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
