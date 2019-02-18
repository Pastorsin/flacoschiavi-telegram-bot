# -*- coding: utf-8 -*-
import urllib.request
import ssl
import textwrap
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod


class Scrap():

    def __init__(self, url):
        self.URL = url

    def start(self):
        self.SOUP = self.create_soup()
        self.clean_text()

    def create_soup(self):
        ssl._create_default_https_context = ssl._create_unverified_context
        request = urllib.request.Request(self.URL)
        html = urllib.request.urlopen(request).read()
        return BeautifulSoup(html, 'html.parser')

    def clean_text(self):
        for br in self.SOUP.find_all('br'):
            br.replace_with('\n')

    def get_info_of(self, subject_name):
        subject_seccion = self.SOUP.find('td', text=subject_name).parent
        return subject_seccion.find_all_next('td')

    def get_start_day(self, subject_name):
        return self.get_info_of(subject_name)[2].text

    def get_schedules(self, subject_name):
        return self.get_info_of(subject_name)[3].text


class Announcement():

    def __init__(self, scrap, subject_name):
        self.SCRAP = scrap
        self.subject_name = subject_name

    def get_announcement(self):
        announcement = self.get_publication() if self.is_published() else 'Nada publicado'
        return self.format(announcement)

    def is_published(self):
        return bool(self.get_publication())

    @abstractmethod
    def get_publication(self):
        pass

    def format(self, announcement):
        lines = announcement.strip().split('\n')
        wraped_text = '\n'.join(
            textwrap.fill(line, 24) for line in lines)
        return '╟' + wraped_text.replace('\n', '\n╟')


class StartDay(Announcement):

    def __init__(self, scrap, subject_name):
        super(StartDay, self).__init__(scrap, subject_name)

    def get_publication(self):
        return self.SCRAP.get_start_day(self.subject_name)


class Schedules(Announcement):

    def __init__(self, scrap, subject_name):
        super(Schedules, self).__init__(scrap, subject_name)

    def get_publication(self):
        return self.SCRAP.get_schedules(self.subject_name)


class Subject():

    def __init__(self, name, scrap):
        self.SCRAP = scrap
        self.name = name
        self.start_day = StartDay(self.SCRAP, self.name)
        self.schedules = Schedules(self.SCRAP, self.name)

    def get_announcement(self):
        start_day = self.get_start_day_announcement()
        schedules = self.get_schedules_annoucement()
        return self.format(start_day, schedules)

    def get_start_day_announcement(self):
        return self.start_day.get_announcement()

    def get_schedules_annoucement(self):
        return self.schedules.get_announcement()

    def format(self, start_day, schedules):
        announcement = '• {}\n╔HORARIOS:\n{}\n╞\n╟COMIENZO:\n{}'.format(
            self.name, schedules, start_day)
        return announcement


class SubjectsList():

    def __init__(self, subject_names, url):
        self.SCRAP = Scrap(url)
        self.subjects = self.get_subjects_list(subject_names)

    def get_subjects_list(self, subject_names):
        return list(self.create_subjects(subject_names))

    def create_subjects(self, subject_names):
        subjects = map(lambda subject_name: Subject(subject_name, self.SCRAP),
                       subject_names)
        return subjects

    def get_announcements(self):
        self.SCRAP.start()
        announcements = map(
            lambda subject: subject.get_announcement(), self.subjects)
        return self.format(announcements)

    def format(self, announcement):
        separator = '\n' + '╚' + ('═' * 25) + '\n'
        return separator.join(announcement) + separator


if __name__ == '__main__':
    subjects = ['Conceptos y Paradigmas de Lenguajes de Programación',
                'Matemática 3',
                'Ingeniería de Software 2',
                'Orientación a Objetos 2']
    url = 'https://gestiondeaulas.info.unlp.edu.ar/cursadas/'
    print(SubjectsList(subjects, url).get_announcements())
