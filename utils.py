#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Contador():
    def __init__(self):
        self.cont = 0

    def inc(self):
        self.cont += 1
        return self.cont
