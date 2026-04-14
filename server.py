from dispatcher import dispatch
from flask import Flask, request
from config import ROUTE

app = Flask(__name__)


@app.route(ROUTE, methods=['POST'])
def telegram_webhook():
    try:
        update = request.get_json()
        dispatch(update)
    except: pass
    return 'ok'
