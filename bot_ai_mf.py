#!/usr/bin/env python3.12
# -*- coding: utf-8 -*-
"""2024-03-05 Fil - Future code Yandex.Practicum
Multi-functional AI-bot
README.md for more

Fil FC AI multi-functional
@fil_fc_ai_mf_bot
https://t.me/fil_fc_ai_mf_bot
"""
__version__ = '0.3'
__author__ = 'Firip Yamagusi'

from time import time, strftime
from random import choice

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

import logging
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, Message

from config import TOKEN_MF
from gpt_ai_mf import count_tokens, get_resp
from db_ai_mf import create_db, create_user, update_user
from db_ai_mf import create_task, update_task, get_stat

bot_name = "Fil FC AI multi-functional | @fil_fc_ai_mf_bot"

# Файл БД
db_file = "ai_mf.db"
db_conn = create_db(db_file)

# Файл лог
log_file = "bot_ai_mf_log.txt"
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt="%F %T",
    filename=log_file,
    filemode="a",
)

logging.warning(f"Бот {bot_name} запущен")

# Для понимания в консоли
print(f"Бот запущен: {bot_name}")
print(f"TOKEN = {TOKEN_MF}")

bot = TeleBot(TOKEN_MF)

# Пустое меню, может пригодиться
hideKeyboard = ReplyKeyboardRemove()

# Два меню для выбора категории и уровня советов
markupSettings = ReplyKeyboardMarkup(
    row_width=3,
    resize_keyboard=True)
Categories = ["Литература", "Живопись", "История"]
Levels = ["Дитятко", "Школяр", "Скубент"]
markupSettings.add(*Categories)
markupSettings.add(*Levels)

# Настройки для языковой модели
system_content = {
    Categories[0]:
        'Ты - доброжелательный помощник, который очень хорошо разбирается '
        'в литературе - стилях, персонажах, сюжетах, биографиях авторов, '
        'обстоятельствах появления литературных произведений. '
        'Отвечай не очень длинными предложениями только на русском языке. ',
    Categories[1]:
        'Ты - доброжелательный помощник, который превосходно разбирается '
        'в живописи - художественных стилях и приёмах, сюжетах, героях '
        'полотен, биографиях художников, обстоятельствах создания разных '
        'картин. '
        'Отвечай не очень длинными предложениями только на русском языке. ',
    Categories[2]:
        'Ты - доброжелательный помощник, который отлично разбирается '
        'в мировой истории. Ты знаешь основные эпохи, причины и обстоятельства '
        'их смены. Знаешь даты событий, годы жизни исторических личностей, '
        'взаимосвязи родственные, соседские, политические. Также знаешь, как '
        'устроена работа историка: что является фактом, на какие источники '
        'можно опираться в суждениях, какими методами исследуют прошлое. '
        'Отвечай не очень длинными предложениями только на русском языке. ',
}
assistant_content = {
    Levels[0]:
        'Используй слова и фразы, понятные даже маленькому ребёнку. Старайся '
        'переформулировать сложные научные термины. Предполагай, что перед '
        'тобой с очень маленьким кругозором и жизненным опытом. ',
    Levels[1]:
        'Отвечай как ребёнку-подростку. Он уже неплохо понимает, как устроены '
        'человеческие отношения, что такое мораль. Но при этом избегай в '
        'своих ответах взрослых тем, излишней жестокости или откровенности. ',
    Levels[2]:
        'Отвечай максимально серьёзно и по делу, как будто перед тобой '
        'очень взрослый и эрудированный человек. Твоя информация должна быть '
        'ему полезна, а значит очень точная и не окрашенная эмоционально. ',
}

# Два популярных запроса: more и break
markup = ReplyKeyboardMarkup(
    row_width=2,
    resize_keyboard=True)
markup.add(*["more", "break", ])

# Глобальные переменные.
# user_data пригодится даже после перехода на SQLite
user_data = {}
max_tokens_in_task = 37


# Часто придётся извиняться за медленный сервер
def send_please_be_patient_message(user_id):
    bot.send_message(
        user_id, '🙏🏻 <b>Я медленная языковая модель, запасись терпением</b>',
        parse_mode="HTML")


# Проверка наличия записи для данного пользователя
def check_user(user_id):
    global user_data, db_conn
    if user_id not in user_data:
        user_data[user_id] = {}
        user_data[user_id]['user_id'] = user_id
        user_data[user_id]['category'] = "История"
        user_data[user_id]['level'] = "Школяр"
        user_data[user_id]['current_task_id'] = 0
        user_data[user_id]['task'] = ""
        user_data[user_id]['answer'] = ""
        user_data[user_id]['busy'] = False
        user_data[user_id]['t_start'] = 0
        user_data[user_id]['t_result'] = 0
        if create_user(db_conn, user_data[user_id]):
            logging.warning(f"Пользователь создан: user_id={user_id}")
        else:
            update_user(db_conn, user_data[user_id])
            logging.warning(f"Пользователь обновлён: user_id={user_id}")


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(m: Message):
    user_id = m.from_user.id
    check_user(user_id)
    bot.send_message(
        user_id,
        '✌🏻 Привет! Я бот с искусственным интеллектом.\n\n'
        'Подскажу тебе всякое разное на мои любимые темы:\n'
        '<b>✍🏻 ЛИТЕРАТУРА</b>,\n<b>🖼 ЖИВОПИСЬ</b>,\n<b>📜 ИСТОРИЯ</b>.\n\n'
        'Выбери также уровень моих ответов:\n'
        'как для 👶🏻 <b>ДИТЯТКИ неразумного</b>,\n'
        'как для 👦🏼 <b>подростка-ШКОЛЯРА несносного</b>, али\n'
        'как для 👨🏻‍🎓 <b>зазнайки-СКУБЕНТА</b>.\n\n'
        'Выбрать тему и уровень можешь в настройках: /settings',
        parse_mode="HTML",
        reply_markup=hideKeyboard)


# Обработчик команды /settings
@bot.message_handler(commands=['settings'])
def handle_settings(m: Message):
    user_id = m.from_user.id
    check_user(user_id)
    bot.send_message(
        user_id,
        'Выбери категорию и уровень моих советов. '
        'По умолчанию я рассказываю про <i>ИСТОРИЮ</i> как для '
        '<i>отрока-ШКОЛЯРА</i>\n. '
        f'Сейчас выбрано:\n'
        f'Категория: <b>{user_data[user_id]['category']}</b>\n'
        f'Уровень: <b>{user_data[user_id]['level']}</b>',
        parse_mode="HTML",
        reply_markup=markupSettings)
    bot.register_next_step_handler(m, set_settings)


def set_settings(m: Message):
    global db_conn
    user_id = m.from_user.id
    check_user(user_id)
    if m.text not in Categories and m.text not in Levels:
        logging.warning(
            f"Пользователь user_id={user_id} не смог изменить настройки")
        bot.send_message(
            user_id,
            'Ошибка: нет такого уровня или категории. Попробуйте ещё раз',
            parse_mode="HTML",
            reply_markup=hideKeyboard)
        bot.register_next_step_handler(m, handle_settings)
        return
    else:
        if m.text in Categories:
            user_data[user_id]['category'] = m.text
        if m.text in Levels:
            user_data[user_id]['level'] = m.text
    update_user(db_conn, user_data[user_id])
    bot.send_message(
        user_id,
        f'Сейчас выбрано:\n'
        f'Категория <b>{user_data[user_id]['category']}</b>\n'
        f'Уровень: <b>{user_data[user_id]['level']}</b>',
        parse_mode="HTML",
        reply_markup=hideKeyboard)


# Обработчик команды /help
@bot.message_handler(commands=['help'])
def handle_help(m: Message):
    user_id = m.from_user.id
    check_user(user_id)
    bot.send_message(
        user_id,
        'Хочешь вспомнить годы жизни Чехова или узнать отчество '
        'Екатерины Великой?\n'
        'Во-первых, ты - молодец!\n'
        'Во-вторых, выбери в настройках (/settings) нужную категорию и '
        'уровень пояснений, а потом смело задавай свой вопрос!\n\n'
        'П-с-с. Ещё есть сИкретная команда /debug\n\n'
        'Примеры запросов:\n'
        '-<i> Кто и зачем исследовал русло реки Енисей?</i>\n'
        '-<i> Если бы ты был печенегом, ты бы терзал Русь?</i>\n'
        '-<i> Почему Айвазовский сбрил усы?</i>\n'
        '-<i> Почему утопили Му-Му, а не барыню?</i>\n'
        '-<i> С тебя при цифре 37 в момент слетает хмель?</i>\n'
        '-<i> Назови всех поэтов XIX века, рифмующих на глаголы</i>\n',
        parse_mode="HTML",
        reply_markup=hideKeyboard)


# Часть домашнего задания - СИКРЕТНЫЙ вывод отладочной информации
@bot.message_handler(commands=['debug'])
def handle_start(m: Message):
    user_id = m.from_user.id
    check_user(user_id)
    logging.warning(f"{user_id}: Любопытный пользователь запросил лог")

    try:
        with open(log_file, "rb") as f:
            bot.send_document(user_id, f)
    except Exception:
        logging.error(
            f"{user_id}: Не получилось отправить лог-файл пользователю")
        bot.send_message(
            user_id,
            f'Не могу найти лог-файл',
            reply_markup=hideKeyboard)


# Часть домашнего задания - вывод статистики
@bot.message_handler(commands=['stat'])
def handle_stat(m: Message):
    user_id = m.from_user.id
    check_user(user_id)
    logging.warning(f"{user_id}: Любопытный пользователь запросил статистику")

    bot.send_message(
        user_id,
        f'<b>СТАТИСТИКА ИСПОЛЬЗОВАНИЯ БОТА</b>',
        parse_mode="HTML")

    # Простая инфа про пользователей
    ds = get_stat(db_conn, type='users')
    users_by_level = [(f"- на уровне <b>{lvl}</b>: "
                       f"{ds['levels'][lvl]}") for lvl in ds['levels']]
    bot.send_message(
        user_id,
        f'👨‍👩‍👦‍👦 Всего пользователей: <b>{ds["total"]}</b>, в т.ч.:\n\n'
        f'{"\n".join(users_by_level)}',
        parse_mode="HTML")

    top_users = [(f"- <b>uid={uid}</b>: "
                  f"{ds['uids'][uid]} шт.") for uid in ds['uids']]
    bot.send_message(
        user_id,
        f'🏆 Топ-3 пользователей по запросам:\n\n'
        f'{"\n".join(top_users)}',
        parse_mode="HTML")

    # Простая инфа про запросы
    ds = get_stat(db_conn, type='tasks')
    tasks_by_level = [(f"- на уровне <b>{lvl}</b>: "
                       f"{ds['levels'][lvl]}") for lvl in ds['levels']]
    tasks_by_category = [(f"- в категориии <b>{cat}</b>: "
                          f"{ds['category'][cat]}") for cat in ds['category']]
    tasks_by_hours = [(f"- час <b>{h}</b>: "
                       f"{ds['hour'][h]}") for h in ds['hour']]
    bot.send_message(
        user_id,
        f'📊 Всего запросов: <b>{ds["total"]}</b>, в т.ч.:\n\n'
        f'{"\n".join(tasks_by_level)}\n\n'
        f'{"\n".join(tasks_by_category)}',
        parse_mode="HTML")

    # Для понтов график с распределением запросов по часам
    data = ds['hour']
    courses = list(data.keys())
    values = list(data.values())

    fig = plt.figure(figsize=(10, 5))
    ax = fig.gca()
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    # creating the bar plot
    plt.bar(courses, values, color='maroon', width=0.4)

    plt.xlabel("Часы")
    plt.ylabel("Количество запросов")
    plt.title("Распредление запросов по часам в течение дня за всё время")
    plt.savefig('myplot.png')
    bot.send_photo(user_id, photo=open('myplot.png', 'rb'))

    rnd_rzhaka = [
        "Как выглядят птенцы голубей?",
        "Кто написал роман 'Мстители: война без конечностей'?",
        "Зачем у Акинфеева татуировка Репина на ноге?",
        "Какие писатели-близнецы по гороскопу Близнецы?",
        "Кто был толще: Лев Толстой или Алексей Толстой?",
        "Мода на женские усики при Елизавете Петровне",
        "Какой краской нарисовать Луну, чтобы светилась",
        "Лучший стих немецкого поэта, который карлик был",
        "Площадь самой большой картины в Третьяковке",
        "Альтернативные концовки дуэли Онегина и Ленского",
        "Как правильно писать: ИЮНЬ или ИЮЛЬ?",
        "Рецепт запрещённого верескового мёда",
        "Составь гороскоп для дядьки Черномора",
        "Как ныне собирает свои вещи Олег?",
        "Взлом ВК без платно быстро надо русичка дура",
        "В какой серии Поттер целовал жабу",
        "Почему у Рубенса все в складочку?",
        "Зачем эпитеты в эпиграфе на эпитафии",
        "Подбери антоним к антониму",
        "Почему валет червей похож на короля пик?",
        "Левитан и Левитан - родственники?",
        "Красная Шапочка в оригинале умерла?",
        "Придумай запрос сразу в три категории: история, литература и живопись",
    ]
    bot.send_message(
        user_id,
        f'🤣 Самый смешной запрос:\n\n'
        f'{choice(rnd_rzhaka)}',
        parse_mode="HTML",
        reply_markup=hideKeyboard)


# Основная обработка входящих запросов
@bot.message_handler(content_types=["text"])
def handle_ask_gpt(m: Message):
    global user_data, db_conn
    user_id = m.from_user.id
    check_user(user_id)

    # Один раз модель зависла. На всякий случай кнопка для оттопыривания
    if m.text.lower() in ["break", "/break"]:
        task = ""
        user_data[user_id]['current_task_id'] = 0
        user_data[user_id]['task'] = ""
        user_data[user_id]['answer'] = ""
        user_data[user_id]['busy'] = False
        err_msg = f"{user_id}: пользователь запросил BREAK"
        logging.warning(err_msg)
        bot.send_message(
            user_id,
            'Прерываю обработку текущего запроса.\n'
            'Подожди секундочку и сформулируй новый запрос.')
        return

    # Чтобы не спамил запросами
    if user_data[user_id]['busy']:
        err_msg = f"{user_id}: слишком частые запросы"
        logging.warning(err_msg)
        bot.send_message(
            user_id,
            f"❎ Пожалуйста, дождись результата для текущего запроса.\n"
            f"(начат {time() - user_data[user_id]['t_start']:0.2f} сек назад)")
        return

    # Ругаемся, если слишком много токенов в запросе
    try:
        if count_tokens(m.text) > max_tokens_in_task:
            err_msg = f"{user_id}: запрос слишком длинный"
            logging.warning(err_msg)
            bot.send_message(
                user_id,
                'ℹ️ GPT сложно обработать длинный запрос. Укороти его.')
            return
    except Exception as e:
        err_msg = f"{user_id}: ошибка функции, вычисляющей токены"
        logging.error(err_msg)
        bot.send_message(
            user_id,
            f'❎ Error: {e}')
        return

    # Если просит продолжить ответ
    if m.text.lower() in ["more", "continue", "/more", "/continue"]:
        if not user_data[user_id]['task']:
            err_msg = f"{user_id}: Запрос продолжения при пустой задаче"
            logging.warning(err_msg)
            bot.send_message(
                user_id,
                f'Продолжить? Но у меня сейчас нет задач!',
                parse_mode="HTML")
            return
        else:
            bot.send_message(
                user_id,
                '...продолжаю...')
    else:
        user_data[user_id]['task'] = m.text
        user_data[user_id]['answer'] = ""
        user_data[user_id]['t_start'] = time()
        user_data[user_id]['current_task_id'] = (
            create_task(db_conn, user_data[user_id]))
        update_user(db_conn, user_data[user_id])
        logging.warning(f"{user_id}: Новая задача "
                        f"task_id={user_data[user_id]['current_task_id']}")
        bot.send_message(
            user_id,
            f'Новая задача: <i>{user_data[user_id]['task']}</i>',
            parse_mode="HTML")

    user_data[user_id]['busy'] = True

    # Предупреждаем, что будет долго
    send_please_be_patient_message(user_id)

    # Проверенный кусок кода API GPT в консоли
    user_data[user_id]['t_start'] = time()
    resp = get_resp(
        system_content[user_data[user_id]['category']],
        assistant_content[user_data[user_id]['level']],
        user_data[user_id]
    )
    user_data[user_id]['t_result'] = time() - user_data[user_id]['t_start']

    # Обрабатываем ответ на случай ошибок
    if resp.status_code == 200 and 'choices' in resp.json():
        result = resp.json()['choices'][0]['message']['content']
        result = result.strip()
        if result == "":
            err_msg = f"{user_id}: GPT вернула пустую строку"
            logging.warning(err_msg)
            bot.send_message(
                user_id,
                'ℹ️ Ответ закончен (модель вернула пустую строку)')
        # Вот в этой веточке успешный результат - показываем в телеграме
        else:
            user_data[user_id]['answer'] += result
            update_task(db_conn, user_data[user_id])
            bot.send_message(
                user_id,
                f"[{user_data[user_id]['t_result']:.2f} сек]\n\n"
                f"{result}",
                parse_mode="HTML",
                reply_markup=markup)
    else:
        err_msg = f"{user_id}: GPT не отвечает на запросы. Попробуйте break"
        logging.error(err_msg)
        logging.error(resp.json())
        bot.send_message(
            user_id,
            f'{err_msg}.\n'
            f'Ошибка: <b>{resp.json()}</b>',
            parse_mode="HTML")

    user_data[user_id]['busy'] = False


# Запуск бота
bot.infinity_polling()
