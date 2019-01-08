#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import datetime
from telegram import MessageEntity
from modules.members import MembersCollection
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters


class VotesManagment():
    """docstring for VotesManagment"""

    def __init__(self, updater):
        self.votes = []
        self.MAX_VOTES = 10
        self.RESET_TIME = datetime.datetime.strptime('00:00', '%H:%M')
        self.add_jobs(updater.job_queue)

    def add_jobs(self, job_queue):
        """Init jobs"""
        job_queue.run_daily(self.reset_votes, self.RESET_TIME.time())

    def reset_votes(self, bot, update):
        """Reset votes to zero"""
        self.votes = []

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
        t = (self.RESET_TIME - datetime.timedelta(
            hours=datetime.datetime.today().hour,
            minutes=datetime.datetime.today().minute))
        h = t.hour
        m = t.minute
        return 'Te quedaste sin votos. Volvé en {}hs {}m masomeno'.format(h, m)


class MentionManagment():
    """docstring for ClassName"""

    def __init__(self, updater, vote):
        self.add_handlers(updater.dispatcher)
        self.vote = vote
        self.score = ScoresManagment(updater)

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

    def __init__(self, updater, vote):
        self.mention_type = MessageEntity.TEXT_MENTION
        super(TextMention, self).__init__(updater, vote)

    def get_user_id(self, update):
        """Returns user id"""
        return self.get_mention_offset_zero(update).user.id


class UsernameMention(MentionManagment):

    def __init__(self, updater, vote):
        self.mention_type = MessageEntity.MENTION
        super(UsernameMention, self).__init__(updater, vote)
        self.members = MembersCollection(updater)

    def get_user_id(self, update):
        """Returns user id"""
        username = self.get_first_word(update)[1:]
        group_id = update.message.chat.id
        return self.members.get_by_username(group_id, username)


class ScoresManagment():

    def __init__(self, updater):
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

    def get_score(self, username, update):
        """Returns the score extracted from message"""
        message = update.message.text.split()
        message.remove(username)
        return message[0]

    def get_score_data(self):
        """Return score json."""
        with open(os.path.join('data', 'scores.json'), 'r') as scores:
            return json.load(scores)

    def is_valid_score(self, username, update):
        """Returns if the mention is followed by a plus
        sign or minus sign and a number"""
        score = self.get_score(username, update)
        return (score[0] in '+-') and score[1:].isdigit()

    def is_between(self, username, update):
        """Returns if score is in max and min range score"""
        score = int(self.get_score(username, update))
        return score in range(self.MIN, self.MAX + 1)

    def scores_list(self, bot, update):
        """Send a message when the command /puntajes is issued."""
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

    def save_score(self, update, username, user_key):
        """Save scores data in JSON"""
        group_key = update.message.chat.id
        score_value = int(self.get_score(username, update))
        scores_json = self.get_score_data()
        with open(os.path.join('data', 'scores.json'), 'w') as scores:
            if (group_key in scores_json) and (user_key in scores_json[group_key]):
                scores_json[group_key][user_key] += score_value
            elif (group_key in scores_json):
                scores_json[group_key][user_key] = score_value
            else:
                scores_json[group_key] = {user_key: score_value}
            json.dump(scores_json, scores, ensure_ascii=False)
