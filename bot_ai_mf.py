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

import logging
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, Message

from config import TOKEN_MF
from gpt_ai_mf import count_tokens, get_resp

bot_name = "Fil FC AI multi-functional | @fil_fc_ai_mf_bot"
# Для понимания в консоли
log_file = "bot_ai_mf_log.txt"
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt="%F %T",
    filename=log_file,
    filemode="w",
)

logging.warning(f"Бот {bot_name} запущен")
logging.warning(f"TOKEN = {TOKEN_MF}")

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

system_content = {
    Categories[0]:
        'Ты - доброжелательный помощник, который очень хорошо разбирается '
        'в литературе - стилях, персонажах, сюжетах, биографиях авторов, '
        'обстоятельствах появления литературных произведений. '
        'Отвечай не очень длинными предложениями только на русском языке.',
    Categories[1]:
        'Ты - доброжелательный помощник, который превосходно разбирается '
        'в живописи - художественных стилях и приёмах, сюжетах, героях '
        'полотен, биографиях художников, обстоятельствах создания разных '
        'картин. '
        'Отвечай не очень длинными предложениями только на русском языке.',
    Categories[2]:
        'Ты - доброжелательный помощник, который отлично разбирается '
        'в мировой истории. Ты знаешь основные эпохи, причины и обстоятельства '
        'их смены. Знаешь даты событий, годы жизни исторических личностей, '
        'взаимосвязи родственные, соседские, политические. Также знаешь, как '
        'устроена работа историка: что является фактом, на какие источники '
        'можно опираться в суждениях, какими методами исследуют прошлое. '
        'Отвечай не очень длинными предложениями только на русском языке.',
}
assistant_content = {
    Levels[0]:
        'Используй слова и фразы, понятные даже маленькому ребёнку. Старайся '
        'переформулировать сложные научные термины. Предполагай, что перед '
        'тобой с очень маленьким кругозором и жизненным опытом.',
    Levels[1]:
        'Отвечай как ребёнку-подростку. Он уже неплохо понимает, как устроены '
        'человеческие отношения, что такое мораль. Но при этом избегай в '
        'своих ответах взрослых тем, излишней жестокости или откровенности.',
    Levels[2]:
        'Отвечай максимально серьёзно и по делу, как будто перед тобой '
        'очень взрослый и эрудированный человек. Твоя информация должна быть '
        'ему полезна, а значит очень точная и не окрашенная эмоционально.',
}

# Два популярных запроса: more и break
markup = ReplyKeyboardMarkup(
    row_width=2,
    resize_keyboard=True)
markup.add(*["more", "break", ])

user_data = {}
max_tokens_in_task = 50


# Часто придётся извиняться за медленный сервер
def send_please_be_patient_message(user_id):
    bot.send_message(
        user_id, '🙏🏻 <b>Я медленная языковая модель, запаситесь терпением</b>',
        parse_mode="HTML")


# Проверка наличия записи для данного пользователя
def check_user(user_id):
    global user_data
    if user_id not in user_data:
        logging.warning(f"Пользователь создан: user_id={user_id}")
        user_data[user_id] = {}
        user_data[user_id]['category'] = "История"
        user_data[user_id]['level'] = "Школяр"
        user_data[user_id]['task'] = ""
        user_data[user_id]['answer'] = ""
        user_data[user_id]['busy'] = False
        user_data[user_id]['t_start'] = 0
        user_data[user_id]['t_result'] = 0


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


# Обработчик команды /help
@bot.message_handler(commands=['settings'])
def handle_settings(m: Message):
    user_id = m.from_user.id
    check_user(user_id)
    bot.send_message(
        user_id,
        'Выбери категорию и уровень моих советов. '
        'По умолчанию я рассказываю про <i>ИСТОРИЮ</i> как для '
        '<i>отрока-ШКОЛЯРА</i>.'
        f'Сейчас выбрано:\n'
        f'Категория <b>{user_data[user_id]['category']}</b>\n'
        f'Уровень: <b>{user_data[user_id]['level']}</b>',
        parse_mode="HTML",
        reply_markup=markupSettings)
    bot.register_next_step_handler(m, set_settings)


def set_settings(m: Message):
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
        'Айвазовского?\n'
        'Во-первых, ты - молодец!\n'
        'Во-вторых, выбери в настройках (/settings) нужную категорию и '
        'уровень пояснений, а потом смело задавай свой вопрос!\n\n'
        'П-с-с. Ещё есть сИкретная команда /debug',
        parse_mode="HTML",
        reply_markup=hideKeyboard)


# Часть домашнего задания - СИКРЕТНЫЙ вывод отладочной информации
@bot.message_handler(commands=['debug'])
def handle_start(m: Message):
    user_id = m.from_user.id
    check_user(user_id)

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


# Основная обработка входящих запросов
@bot.message_handler(content_types=["text"])
def handle_ask_gpt(m: Message):
    global user_data
    user_id = m.from_user.id
    check_user(user_id)

    # Один раз модель зависла. На всякий случай кнопка для оттопыривания
    if m.text.lower() in ["break", "/break"]:
        task = ""
        user_data[user_id]['task'] = ""
        user_data[user_id]['answer'] = ""
        user_data[user_id]['busy'] = False
        err_msg = f"{user_id}: пользователь запросил BREAK"
        logging.warning(err_msg)
        bot.send_message(
            user_id,
            'Что-то пошло не так!\n'
            'Подождите секундочку и сформулируйте новый запрос.')
        return

    # Чтобы не спамил запросами
    if user_data[user_id]['busy']:
        err_msg = f"{user_id}: слишком частые запросы"
        logging.warning(err_msg)
        bot.send_message(
            user_id,
            f"❎ Пожалуйста, подождите результата текущего запроса.\n "
            f"(начат {time() - user_data[user_id]['t_start']:0.2f} сек назад)")
        return

    # Ругаемся, если слишком много токенов в запросе
    try:
        if count_tokens(m.text) > max_tokens_in_task:
            err_msg = f"{user_id}: запрос слишком длинный"
            logging.warning(err_msg)
            bot.send_message(
                user_id,
                'ℹ️ GPT сложно обработать длинный запрос. Укоротите его.')
            return
    except Exception as e:
        err_msg = f"{user_id}: ошибка функции, вычисляющей токены"
        logging.warning(err_msg)
        bot.send_message(
            user_id,
            f'❎ Error: {e}')
        return

    # Если просит продолжить ответ
    if m.text.lower() in ["more", "continue", "/more", "/continue"]:
        if not user_data[user_id]['task']:
            err_msg = strftime("%F %T") + ": asked for more while task is empty"
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
        bot.send_message(
            user_id,
            f'Моя задача: <i>{user_data[user_id]['task']}</i>',
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
        if result == "":
            err_msg = f"{user_id}: GPT вернула пустую строку"
            logging.error(err_msg)
            bot.send_message(
                user_id,
                'ℹ️ Ответ закончен (модель вернула пустую строку)')
        # Вот в этой веточке успешный результат - показываем в телеграме
        else:
            user_data[user_id]['answer'] += result
            bot.send_message(
                user_id,
                f"[{user_data[user_id]['t_result']:.2f} сек]\n\n"
                f"{result.strip()}" ,
                parse_mode="HTML",
                reply_markup=markup)
    else:
        err_msg = f"{user_id}: GPT не отвечает на запросы. Попробуйте break"
        logging.error(err_msg)
        bot.send_message(
            user_id,
            f'{err_msg}.\n'
            f'Ошибка: <b>{resp.json()}</b>',
            parse_mode="HTML")

    user_data[user_id]['busy'] = False


# Запуск бота
bot.infinity_polling()
