'''
Arquivo que será chamado no início da aplicação
'''

from Message import Message
import telepot
from telepot.loop import MessageLoop
from config import WEBHOOK

import urllib3
from bot import my_bot

from dispatcher import register_handler, dispatch
from handlers import handlers

# Importar o servidor é suficiente para rodar o arquivo
from server import app

for handler in handlers:
    register_handler(handler=handler)

if __name__ == "__main__":
    my_bot.setWebhook()
    print("Rodando em ambiente de desenvolvimento")
    def f(m: Message):
        print(m)
        dispatch({"message": m})

    MessageLoop(my_bot, f).run_forever()

else:
    proxy_url = 'http://proxy.server:3128'
    telepot.api._pools = {
        'default': urllib3.ProxyManager(
            proxy_url=proxy_url,
            num_pools=3,
            maxsize=10,
            retries=False,
            timeout=30),
    }
    telepot.api._onetime_pool_spec = (urllib3.ProxyManager, 
    dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))

    my_bot.setWebhook(WEBHOOK, max_connections=1)
