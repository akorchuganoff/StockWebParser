import json

import telebot
from flask import Flask
from flask import request, abort
import requests

import config
from parser import get_stats

# Создание приложения фласк и бота по токену
app = Flask(__name__)
bot = telebot.TeleBot(config.token)


# Чтобы подвязать вебхуки - сначала удалите их из бота (если уже были) и установите новые
bot.remove_webhook()
bot.set_webhook("https://0461-95-64-138-66.eu.ngrok.io/")

# Вьюшка, отвечающая за получение вебхуков от телеграма
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)


@bot.message_handler(commands=['start'])
def start(message):
    text = """Привет,\nЯ бот помошник на рынке акций. Я умею находить цену акций, а также читать новости о компании.
Чтобы добавить бумагу в портфель напиши /add <тикер на бирже>
Чтобы получить полную информацию - напиши /stats <ticker>"""
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['add'])
def add(message):
    pass


@bot.message_handler(commands=['stats'])
def stats(message):
    ticker = message.text.split(maxsplit=1)[1]  # В переменной будет всё,что идёт после /stats
    bot.send_message(message.chat.id, f'Ticker = {ticker}')
    answer = get_stats(ticker)
    text = f"```{json.dumps(answer)}```"
    bot.send_message(message.chat.id, text)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4567, debug=False)
