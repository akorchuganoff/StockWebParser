import json
import os
import time
from datetime import datetime

import telebot
from flask import Flask, request
from flask import abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON

import config
from parser import get_stats, get_prices
from response_maker import make_pdf_from_json

# Создание приложения фласк и бота по токену
app = Flask(__name__)
app.app_context().push()

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'server.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    chat_id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    portfolio = db.Column(JSON)

    def __repr__(self):
        return f"User {self.chat_id}"


bot = telebot.TeleBot(config.token)


# Чтобы подвязать вебхуки - сначала удалите их из бота (если уже были) и установите новые
# bot.remove_webhook()
# bot.set_webhook("https://7a53-95-64-138-66.eu.ngrok.io/")

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
Чтобы получить цену бумаг в портфеле - напиши /prices (После вызова этого метода - последние цены в системе - обновятся)
Чтобы удалить бумагу из портфеля - напиши /delete <ticker>
Чтобы получить полную информацию - напиши /stats <ticker>"""
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['add'])
def add(message):
    try:
        with app.app_context():
            ticker = message.text.split(maxsplit=1)[1]  # В переменной будет всё,что идёт после /stats
            prices = get_prices([ticker])
            if prices[ticker] == "Не смог найти":
                bot.send_message(message.chat.id, f'Не смог найти информацию по данной бумаге. Проверьте Тикер')
                return
            bot.send_message(message.chat.id, f'Ticker = {ticker}')
            user = User.query.filter_by(chat_id=message.chat.id).first()
            if user is None:

                user = User(
                    chat_id=message.chat.id,
                    portfolio=json.dumps(prices),
                    firstname=message.from_user.first_name,
                    lastname=message.from_user.last_name
                )
            else:
                data = json.loads(user.portfolio)
                data[ticker] = prices[ticker]
                user.portfolio = json.dumps(data)
            db.session.add(user)
            db.session.commit()
            bot.send_message(message.chat.id, f'Ticker = {ticker} - added to your portfolio')
    except Exception as ex:
        print(ex)


@bot.message_handler(commands=['prices'])
def prices(message):
    try:
        text = "Цены в системе обновлены\n"
        text += "Цены акций в формате:\n'Тикер - Последняя цена - Текущая цена - Разница'\n"
        with app.app_context():
            user = User.query.filter_by(chat_id=message.chat.id).first()
            if user is None:
                bot.send_message(message.chat.id, "У вас еще нет портфеля. Создайте его командой /add")
            bot.send_message(message.chat.id, "Собираем данные, ожидайте")
            portfolio = json.loads(user.portfolio)
            keys = portfolio.keys()
            prices = get_prices(keys)
            print(prices)

            for k, v in portfolio.items():
                text += f"{k} - {v} - {prices[k]} - {float(prices[k]) / float(v) * 100 - 100}%\n"
            bot.send_message(message.chat.id, text)
            user.portfolio = json.dumps(prices)
            db.session.add(user)
            db.session.commit()
    except Exception as ex:
        print(ex)


@bot.message_handler(commands=['stats'])
def stats(message):
    ticker = message.text.split(maxsplit=1)[1]  # В переменной будет всё,что идёт после /stats
    bot.send_message(message.chat.id, f'Ticker = {ticker}')
    answer = get_stats(ticker)
    if answer == "Не смог найти":
        bot.send_message(message.chat.id, f'Не смог найти информацию по данной компании. Проверьте тикер')
        return
    text = "Сейчас пришлю файл с подробным отчетом о компании"

    filename = f'{ticker}_{message.chat.id}_{datetime.now().strftime("%Y-%m-%d_%H_%M")}.pdf'
    make_pdf_from_json(answer, filename)

    bot.send_message(message.chat.id, text)
    file = open(filename, 'rb')
    bot.send_document(message.chat.id, file)
    time.sleep(3)
    os.remove(filename)


@bot.message_handler(commands=['delete'])
def delete(message):
    ticker = message.text.split(maxsplit=1)[1]  # В переменной будет всё,что идёт после /stats
    try:
        with app.app_context():
            user = User.query.filter_by(chat_id=message.chat.id).first()
            if user is None:
                bot.send_message(message.chat.id, "У вас нет этой бумаги в портфеле")
                return
            data = json.loads(user.portfolio)
            if ticker not in data.keys():
                bot.send_message(message.chat.id, "У вас нет этой бумаги в портфеле")
                return
            del data[ticker]
            user.portfolio = json.dumps(data)
            db.session.add(user)
            db.session.commit()
            bot.send_message(message.chat.id, "Бумага успешно удалена")
    except Exception as ex:
        print(ex)


def main():
    ## if we have a mistake, and want to drop all db
    # with app.app_context():
    #     db.drop_all()
    #     db.create_all()
    app.run(host='0.0.0.0', port=4567, debug=False)


if __name__ == "__main__":
    main()
