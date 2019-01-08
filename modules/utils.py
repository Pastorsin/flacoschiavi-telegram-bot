#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import datetime

class Utils():

    def to_regex(self, word):
        w = ''
        for ch in word:
            w += '[{}{}]'.format(ch.lower(), ch.upper())
        return '.*{}\\.*'.format(w)

    def tomorrow_day(self):
        """Return the week day of tomorrow day."""
        return (datetime.datetime.today() + datetime.timedelta(1)).weekday()

    def random_time(self):
        """Return a Time object with random hour and minute."""
        hour = str(random.randint(0, 23))
        minute = str(random.randint(0, 59))
        return datetime.datetime.strptime(hour + ':' + minute, '%H:%M').time()
