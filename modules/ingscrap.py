# -*- coding: utf-8 -*-
import threading
import requests
import json
import time


class Scrap():
	def __init__(self, bot):
		self.BOT = bot
		self.CHAT = '-370665707'
		self.TOTAL = 15
		self.start()

	def start(self):	
		while True:
			announcements = self.get_announcements()
			if announcements['total'] > self.TOTAL:
				print('Sin novedades')
				self.send_messages(announcements)
				break
			time.sleep(5)

	def get_announcements(self):
		request = requests.get('https://gestiondeaulas.info.unlp.edu.ar/cartelera/data/0/1?idMateria=76', verify=False)
		return json.loads(request.content)

	def send_messages(self, announcements):
		self.BOT.send_message(chat_id=self.CHAT ,text=announcements['mensajes'][0]['cuerpo'])
		for x in range(10):
			self.BOT.send_message(chat_id=self.CHAT, text='A inscribirse!!!!')