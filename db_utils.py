'''
Funções referentes à criação e edição de bancos de dados dos bots
'''

import json
import os

def get_db(data_name: str = 'bot_data') -> dict:
    '''Retorna o banco de dados solicitado em formato de dicionário.'''
    '''Se ele não existir, cria o banco de dados'''

    if not os.path.exists(data_name + '.json'):
        with open(data_name + '.json', 'w', encoding='utf8') as db:
            json.dump({}, db)
        return {}
    
    db = {}
    with open(data_name + '.json', 'r', encoding='utf8') as db:
        db = json.load(db)
    return db


def save_db(data: dict, data_name: str = 'bot_data') -> None:
    '''Reescreve o banco de dados solicitado'''
    if not data:
        return

    with open(data_name + '.json', 'w', encoding='utf8') as db:
        json.dump(data, db, ensure_ascii=False)