#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random


cont_xd = [0]


def amigos():
    return 'Vos no tenés amigos pelotudo.'


def quien():
    return 'Tu vieja.'


def pocho():
    return 'PochoOoOOOoOoOoOOoOoo'


def porno():
    PORN = ("petardas", "pornhub", "serviporno", "xvideos", "redtube")
    return 'http://www.{0}.com/'.format(random.choice(PORN))


def gracias():
    return 'De nada campeón.'


def xd():
    cont_xd[0] += 1
    return 'Me dijeron {0} veces XD.'.format(cont_xd[0])
