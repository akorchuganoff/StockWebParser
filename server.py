import telebot
from flask import Flask
from flask import request, abort

import config
import requests

# Создание приложения фласк и бота по токену
app = Flask(__name__)
bot = telebot.TeleBot(config.token)

## Чтобы подвязать вебхуки - сначала удалите их из бота (если уже были) и установите новые
# bot.remove_webhook()
# bot.set_webhook("https://6723-95-64-138-66.eu.ngrok.io/")

#Вьюшка, отвечающая за получение вебхуков от телеграма
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
    bot.send_message(message.chat.id, '')



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4567, debug=False)
