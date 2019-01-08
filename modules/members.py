#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import MessageHandler, Filters


class MembersCollection():

    def __init__(self, updater):
        self.members = {}
        self.add_handlers(updater.dispatcher)

    def add_handlers(self, dp):
        dp.add_handler(MessageHandler(Filters.text, self.save_member))
        dp.add_handler(MessageHandler(
            Filters.status_update.new_chat_members, self.save_member))
        dp.add_handler(MessageHandler(
            Filters.status_update.left_chat_member, self.delete_member))

    def save_member(self, bot, update):
        group_key = update.message.chat.id
        user = update.message.from_user
        if group_key not in self.members:
            self.members[group_key] = []
        if user in self.members[group_key]:
            self.members[group_key].remove(user)
        self.members[group_key].append(user)
        print(self.members)

    def is_registred(self, group_key, user):
        return group_key in self.members and user in self.members[group_key]

    def delete_member(self, bot, update):
        group_key = update.message.chat.id
        user = update.message.from_user
        if self.is_registred(group_key, user):
            self.members[group_key].remove(user)

    def get_by_username(self, group_key, username):
        if group_key in self.members:
            member = list(filter(lambda user: user.username ==
                                 username, self.members[group_key]))
            return member.pop().id if member else None
