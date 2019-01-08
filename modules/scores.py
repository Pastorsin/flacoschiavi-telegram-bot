#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import random
import datetime
from modules.utils import Utils
from modules.members import MembersCollection
from telegram import MessageEntity
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters


class VotesManagment():

    def __init__(self, updater):
        self.votes = []
        self.MAX_VOTES = 10
        self.add_jobs(updater.job_queue)

    def add_jobs(self, job_queue):
        """Init jobs"""
        job_queue.run_daily(self.reset_votes, datetime.datetime.today())

    def reset_votes(self, bot, job):
        """Reset votes to zero"""
        # Reset votes
        self.votes = []
        # Send Arieeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeel
        bot.send_message(chat_id='-249336357',
                         text=('Ari' + ('e' * random.randint(8, 25) + 'l')))
        # Remove actual job from job queue
        job.schedule_removal()
        # Add new callback for tomorrow with a random hour
        random_time = Utils().random_time()
        tomorrow_day = Utils().tomorrow_day()
        job.job_queue.run_daily(
            self.reset_votes, random_time, (tomorrow_day, ))

    def add_vote(self, user_id):
        """Add vote to a user"""
        self.votes.append(user_id)

    def user_votes(self, user_id):
        """Returns user votes"""
        return self.MAX_VOTES - self.votes.count(user_id)

    def can_vote(self, update):
        """Returns if user can vote"""
        return self.votes.count(update.message.from_user.id) < self.MAX_VOTES

    def msg_cant_vote(self):
        """Returns a message if user cant vote"""
        return 'Te quedaste sin votos. Volvé cuando el flaco diga Arieeeeeeel'


class MentionManagment():

    def __init__(self, updater, vote, storage):
        self.add_handlers(updater.dispatcher)
        self.vote = vote
        self.score = ScoresManagment(updater, storage)

    def add_handlers(self, dispatcher):
        """Init bot handlers"""
        dispatcher.add_handler(MessageHandler(
            (Filters.entity(self.mention_type)), self.reply))

    def reply(self, bot, update):
        """Reply with failure or successful message of event"""
        update.message.reply_text(self.get_message(bot, update))

    def checks(self):
        """Returns a dict with {check_callback:msg_error}"""
        return {
            self.is_first_word: 'Mencionaste a alguien, ' +
                                'acordate que lo podes puntuar <.<',
            self.is_member: 'No es miembro humano del grupo jujuj',
            self.is_not_same_user: 'No te podes votar a vos mismo ' +
                                'cabeza de plumero',
            self.is_valid_score: 'Puntaje inválido maquinola.' +
                                ' @username puntaje',
            self.is_between: 'AAAAA FUERA DEL RANGOOO',
            self.can_vote: self.vote.msg_cant_vote()
        }

    def send_successful_message(self, update):
        """Returns a succesful message"""
        fullname = update.message.chat.get_member(
            self.get_user_id(update)).user.full_name
        votes = self.vote.user_votes(update.message.from_user.id)
        msg = 'Joya!! Voto realizado a {}. Te quedan {} votos'.format(
            fullname, votes)
        print(msg)
        return msg

    def get_message(self, bot, update):
        """Returns the failure or successful message of event"""
        # Check before save score
        for valid_mention, msg in self.checks().items():
            if not valid_mention(update):
                return msg
        # Save score
        self.score.save_score(update, self.get_first_word(
            update), self.get_user_id(update))
        # Add vote of day
        self.vote.add_vote(update.message.from_user.id)
        # Send successful message
        return self.send_successful_message(update)

    def get_mentions_entities(self, update):
        """Returns a dict with (mention:word)"""
        return update.message.parse_entities([self.mention_type])

    def get_mention_offset_zero(self, update):
        """Returns the mention in offset 0"""
        entities = self.get_mentions_entities(update)
        mention = list(filter((lambda mention: mention.offset == 0), entities))
        return mention.pop() if mention else None

    def get_first_word(self, update):
        """Returns the first word of mention"""
        entities = self.get_mentions_entities(update)
        return entities[self.get_mention_offset_zero(update)]

    def is_first_word(self, update):
        """Returns if mention is the first word of message."""
        return bool(self.get_mention_offset_zero(update))

    def is_member(self, update):
        """Returns if user is group member"""
        return bool(self.get_user_id(update))

    def is_valid_score(self, update):
        """Returns if score is valid"""
        username = self.get_first_word(update)
        return self.score.is_valid_score(username, update)

    def is_between(self, update):
        """Returns if score is in max and min range score"""
        username = self.get_first_word(update)
        return self.score.is_between(username, update)

    def is_not_same_user(self, update):
        """Returns if user is not himself"""
        return update.message.from_user.id != self.get_user_id(update)

    def can_vote(self, update):
        """Returns if user can score"""
        return self.vote.can_vote(update)


class TextMention(MentionManagment):

    def __init__(self, updater, vote, storage):
        self.mention_type = MessageEntity.TEXT_MENTION
        super(TextMention, self).__init__(updater, vote, storage)

    def get_user_id(self, update):
        """Returns user id"""
        return self.get_mention_offset_zero(update).user.id


class UsernameMention(MentionManagment):

    def __init__(self, updater, vote, storage):
        self.mention_type = MessageEntity.MENTION
        super(UsernameMention, self).__init__(updater, vote, storage)
        self.members = MembersCollection(updater)

    def get_user_id(self, update):
        """Returns user id"""
        username = self.get_first_word(update)[1:]
        group_id = update.message.chat.id
        return self.members.get_by_username(group_id, username)


class ScoresManagment():

    def __init__(self, updater, storage):
        self.STORAGE = storage
        self.MIN = -25
        self.MAX = 50
        self.add_handlers(updater.dispatcher)

    def add_handlers(self, dispatcher):
        """Init bot handlers"""
        dispatcher.add_handler(CommandHandler("puntajes", self.scores_list))
        dispatcher.add_handler(CommandHandler("help", self.help))

    def help(self, bot, update):
        """Send a message when the command /help is issued."""
        message = open(os.path.join('data', 'score_rules.txt'),
                       'r').read().format(self.MIN, self.MAX)
        update.message.reply_text(message)

    def scores_list(self, bot, update):
        """Send a message when the command /puntajes is issued."""
        chat_id = update.message.chat.id
        if self.STORAGE.is_chat_saved(chat_id):
            update.message.reply_text(self.scores_message(update, chat_id))
        else:
            self.help(bot, update)

    def get_score(self, username, update):
        """Returns the score extracted from message"""
        message = update.message.text.split()
        message.remove(username)
        return message[0]

    def is_valid_score(self, username, update):
        """Returns if the mention is followed by a plus
        sign or minus sign and a number"""
        score = self.get_score(username, update)
        return (score[0] in '+-') and score[1:].isdigit()

    def is_between(self, username, update):
        """Returns if score is in max and min range score"""
        score = int(self.get_score(username, update))
        return score in range(self.MIN, self.MAX + 1)

    def scores_message(self, update, chat_id):
        """Returns the scores list message"""
        msg = '╔\n'
        for user_id, score in self.STORAGE.get_scores(chat_id).items():
            chat = update.message.chat
            fullname = chat.get_member(user_id).user.full_name
            msg += '╟ {} : {} puntos. \n'.format(fullname, score)
        msg += '╚ '
        return msg

    def save_score(self, update, username, user_id):
        """Save scores data"""
        chat_id = update.message.chat.id
        score = int(self.get_score(username, update))
        self.STORAGE.save_score(chat_id, user_id, score)
