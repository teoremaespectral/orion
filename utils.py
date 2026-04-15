'''
Funções com utilidades para o bot
'''

from random import randint
import constants as c

def chance_one_in(n: int):
    ''' Retorna True com uma chance de 1 em n. '''
    return 1 == randint(1, n)

def is_too_little(amount, reference):
    ''' Retorna True se a quantidade for menor que uma fração do valor de referência. '''
    return amount < reference * c.TOO_LITTLE

def is_too_much(amount, reference):
    ''' Retorna True se a quantidade for maior que uma fração do valor de referência. '''
    return amount > reference * c.TOO_MUCH