#!/usr/bin/env python3.12
# -*- coding: utf-8 -*-
"""2024-03-05 Fil - Future code Yandex.Practicum
Multi-functional AI-bot
README.md for more

Fil FC AI multi-functional
@fil_fc_ai_mf_bot
https://t.me/fil_fc_ai_mf_bot
"""
__version__ = '0.2'
__author__ = 'Firip Yamagusi'

from time import strftime

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
max_tokens_in_task = 35


# Часто придётся извиняться за медленный сервер
def send_please_be_patient_message(uid):
    bot.send_message(
        uid, '🙏🏻 <b>This GPT model is very slow, please be patient</b>',
        parse_mode="HTML")


# Проверка наличия записи для данного пользователя
def check_user(uid):
    global user_data
    if uid not in user_data:
        logging.warning(f"Пользователь создан: uid={uid}")
        user_data[uid] = {}
        user_data[uid]['category'] = "История"
        user_data[uid]['level'] = "Школяр"
        user_data[uid]['debug'] = []
        user_data[uid]['task'] = ""
        user_data[uid]['answer'] = ""
        user_data[uid]['busy'] = False


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
            f"Пользователь uid={user_id} не смог изменить настройки")
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
    error_log = "is empty now"
    if user_data[user_id]['debug']:
        error_log = "\n".join(user_data[user_id]['debug'])

    try:
        with open(log_file, "rb") as f:
            bot.send_document(user_id, f)
    except Exception:
        logging.error(
            f"Не получилось отправить лог-файл пользователю uid={user_id}")
        bot.send_message(
            user_id,
            f'Cannot find log file',
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
        err_msg = strftime("%F %T") + ": BREAK for some reason"
        user_data[user_id]['debug'].append(err_msg)
        bot.send_message(
            user_id,
            'Something went wrong!\n'
            'Wait for a while and try another task.')
        return

    # Чтобы не спамил запросами
    if user_data[user_id]['busy']:
        err_msg = strftime("%F %T") + ": SPAM detected"
        user_data[user_id]['debug'].append(err_msg)
        bot.send_message(
            user_id,
            f"❎ Please, don't spam! This task will be ignored.")
        return

    # Ругаемся, если слишком много токенов в запросе
    try:
        if count_tokens(m.text) > max_tokens_in_task:
            err_msg = strftime("%F %T") + ": prompt is too long"
            user_data[user_id]['debug'].append(err_msg)
            bot.send_message(
                user_id,
                'ℹ️ Your prompt is too long. Please try again.')
            return
    except Exception as e:
        err_msg = strftime("%F %T") + ": error while using count_tokens()"
        user_data[user_id]['debug'].append(err_msg)
        bot.send_message(
            user_id,
            f'❎ Error: {e}')
        return

    # Если просит продолжить ответ
    if m.text.lower() in ["more", "continue", "/more", "/continue"]:
        if not user_data[user_id]['task']:
            err_msg = strftime("%F %T") + ": asked for more while task is empty"
            user_data[user_id]['debug'].append(err_msg)
            bot.send_message(
                user_id,
                f'You asked for more? There is no task!',
                parse_mode="HTML")
            return
        else:
            bot.send_message(
                user_id,
                '...I will continue...')
    else:
        user_data[user_id]['task'] = m.text
        user_data[user_id]['answer'] = ""
        bot.send_message(
            user_id,
            f'New task: <i>{user_data[user_id]['task']}</i>',
            parse_mode="HTML")

    user_data[user_id]['busy'] = True

    # Предупреждаем, что будет долго
    send_please_be_patient_message(user_id)

    # Проверенный кусок кода API GPT в консоли
    resp = get_resp(
        system_content[user_data[user_id]['category']],
        assistant_content[user_data[user_id]['level']],
        user_data[user_id]
    )

    # Обрабатываем ответ на случай ошибок
    if resp.status_code == 200 and 'choices' in resp.json():
        result = resp.json()['choices'][0]['message']['content']
        if result == "":
            err_msg = strftime("%F %T") + ": model returned an empty string"
            user_data[user_id]['debug'].append(err_msg)
            bot.send_message(
                user_id,
                'ℹ️ I have said enough.')
        # Вот в этой веточке успешный результат - показываем в телеграме
        else:
            user_data[user_id]['answer'] += result
            bot.send_message(
                user_id,
                result,
                reply_markup=markup)
    else:
        err_msg = strftime("%F %T") + ": GPT is not avaliable now"
        user_data[user_id]['debug'].append(err_msg)
        bot.send_message(
            user_id,
            f'GPT is not avaliable now.\n'
            f'Error message: <b>{resp.json()}</b>',
            parse_mode="HTML")

    user_data[user_id]['busy'] = False


# Запуск бота
bot.infinity_polling()
