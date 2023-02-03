# Simple StockWebParser
This project is a telegram bot written using webhooks. He has a number of commands that are responsible for parsing certain data (bs4), as well as for working with the database (sqlalchemy).

## Этапы разработки
* [Поднятие локального сервера для вебхуков](#server)
* [Написание каркаса бота](#bot)
* [Написание парсера](#parser)
* [Command Handlers](#commands)
* [PDF Maker](#pdf)
* [Database](#db)

<a name="server"></a>
## Поднятие локального сервера для вебхуков
Это довольно сложный этап. Постараюсь изложить все последовательно.
1) Регистрируемся и устанавливаем ngrok [отсюда](https://ngrok.com/)
2) Делаем каркас Flask приложения
3) Запускаем сервер, затем ngrok и получаем ссылку на локалхост от ngrok
4) Создаем каркас бота, пишем следующие 2 строчки, чтобы привязать webhooks:
```python
bot.remove_webhook()
bot.set_webhook("https://7a53-95-64-138-66.eu.ngrok.io/")
#Вставьте ссылку, полученную от ngrok
```
5) Поздравляю, вебхуки подвязаны
<a name="bot"></a>
## Написание каркаса бота
Ничего сверхъестественного. Все делал опираясь на документацию и уроки в открытом доступе.
Например, [1](https://habr.com/ru/post/442800/), [2](https://mastergroosha.github.io/telegram-tutorial/docs/lesson_01/), [3](https://pypi.org/project/pyTelegramBotAPI/)
<a name="parser"></a>
## Написание парсера
В качестве поля для экспериментов выбрал [этот сайт](https://finance.yahoo.com).
Пытался парсить через lxml, но BeautifulSoup4 показался мне эффективнее и проще. 
Создал 2 функции: **get_price** и **get_stats**
##### **get_prise**
> Получает на вход массив тикеров, а возвращает словарь вида {ticker: price}. Если не может найти информацию по тикеру - в этом поле словаря будет соответствующий текст
##### **get_stats**
> Более общая функция. Получает на вход ровно один тикер, и собирает всю информацию о компании со страницы. Возвращает JSONSerializible


<a name="commands"></a>
## Написание Command Handlers
Казалось бы, что в этом сложного. Однако при работе с вебхуками просто так бот не будет получать сообщения. Ему нужно показать откуда их брать. Я долго мучался с этим вопросом и нашел такое решение:
```python
import telebot
from flask import request, abort
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)
```
Также была беда с распознаванием аргумента команды. Поставил костыль, но вроде бы работает
```python
ticker = message.text.split(maxsplit=1)[1]  # В переменной будет всё, что идёт после /stats
```

В остальном - по большей части просто адаптация кода из материалов, приведенных выше
## PDF Maker
В какой-то момент, проект показался мне слишком простым. Я решил усложнить себе жизнь тем, что данные, полученные от парсера при сборе статистики я уложил в pdf файл, который после отправлял пользователю
Мне очень помог [этот урок](https://www.youtube.com/watch?v=euNvxWaRQMY&t=193s). Конечно там было очень много лишнего кода, однако я смог его адаптировать

<a name="db"></a>
## Database
Финальной частью проекта стало написание команд, взаимодействующих с бд. Т.к. основой сервера был Flask - я решил сделать все максимально просто. Я использовал SQLite3 + Flask-SQLalchemy
Возникла сложность с ошибкой
>RuntimeError: working outside of application context

Возникает ощущение, что я опять воткнул костыль, однако ничего более разумного, чем предложенное [здесь](https://stackoverflow.com/questions/34122949/working-outside-of-application-context-flask) я не нашел