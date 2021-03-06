import os
import psycopg2


class DBStorage():

    def __init__(self):
        DATABASE_URL = os.getenv('DATABASE_URL')
        self.conn = psycopg2.connect(DATABASE_URL, sslmode='require')

    def is_chat_saved(self, chat_id):
        cursor = self.conn.cursor()
        sql = 'SELECT * FROM chat WHERE chat_id = {};'.format(chat_id)
        cursor.execute(sql)
        return cursor.fetchone()

    def is_member_saved(self, user_id):
        cursor = self.conn.cursor()
        sql = 'SELECT * FROM member WHERE member_id = {};'.format(user_id)
        cursor.execute(sql)
        return cursor.fetchone()

    def is_chat_member_saved(self, chat_id, user_id):
        cursor = self.conn.cursor()
        sql = 'SELECT * FROM chat_member WHERE member_id = {} and chat_id = {};'.format(
            user_id, chat_id)
        cursor.execute(sql)
        return cursor.fetchone()

    def save_chat(self, chat_id):
        sql = 'INSERT INTO chat (chat_id) VALUES ({});'.format(chat_id)
        self.conn.cursor().execute(sql)
        self.conn.commit()

    def save_member(self, user_id):
        sql = 'INSERT INTO member (member_id) VALUES ({});'.format(user_id)
        self.conn.cursor().execute(sql)
        self.conn.commit()

    def insert_score(self, chat_id, user_id, score):
        sql = '''
        INSERT INTO chat_member (chat_id, member_id, score)
        VALUES ({}, {}, {});'''.format(chat_id, user_id, score)
        self.conn.cursor().execute(sql)

    def update_score(self, chat_id, user_id, score):
        sql = '''
        UPDATE chat_member
        SET score = score + {}
        WHERE chat_id = {} and member_id = {};'''.format(score, chat_id, user_id)
        self.conn.cursor().execute(sql)

    def save_score(self, chat_id, user_id, score):
        if not self.is_chat_saved(chat_id):
            self.save_chat(chat_id)
        if not self.is_member_saved(user_id):
            self.save_member(user_id)
        if not self.is_chat_member_saved(chat_id, user_id):
            self.insert_score(chat_id, user_id, score)
        else:
            self.update_score(chat_id, user_id, score)
        self.conn.commit()

    def get_scores(self, chat_id):
        cursor = self.conn.cursor()
        sql = '''
        SELECT member_id, score
        FROM chat_member as cm
        WHERE cm.chat_id = {};'''.format(chat_id)
        cursor.execute(sql)
        return dict(cursor.fetchall())
