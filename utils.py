'''
Funções com utilidades para o bot
'''

from random import randint

def chance_one_in(n: int):
    return 1 == randint(1, n)