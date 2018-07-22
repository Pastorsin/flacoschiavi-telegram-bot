#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random

with open('sustantivos.txt', 'r') as f:
    NOUNS = tuple(f)
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


def cara_de():
    return '{0} de {1}'.format(random.choice(NOUNS).strip(),
        random.choice(NOUNS).strip())
        
