'''
Arquivo de importação do .env
'''

import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK = os.getenv("WEBHOOK")
ROUTE = os.getenv("ROUTE")