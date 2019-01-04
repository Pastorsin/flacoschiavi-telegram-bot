#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Utils():

    def to_regex(self, word):
        w = ''
        for ch in word:
            w += '[{}{}]'.format(ch.lower(), ch.upper())
        return '.*{}*'.format(w)


