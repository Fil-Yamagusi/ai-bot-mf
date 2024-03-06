#!/usr/bin/env python3.12
# -*- coding: utf-8 -*-
"""2024-03-06 Fil - Future code Yandex.Practicum
Multi-functional AI-bot
README.md for more

SQLite DB functions
"""

import sqlite3


def create_db(db_file):
    db_connection = sqlite3.connect(db_file, check_same_thread=False)
    cursor = db_connection.cursor()

    # Создаем таблицу Users
    # Здесь хранятся текущие значения настроек
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS Users ('
        'user_id INTEGER PRIMARY KEY, '
        'category TEXT, '
        'level TEXT, '
        'current_task_id INTEGER'
        ')'
    )

    # Создаем таблицу Tasks
    # Здесь для статистики хранятся настройки на момент запроса
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS Tasks ('
        'id INTEGER PRIMARY KEY, '
        'user_id INTEGER, '
        'category TEXT, '
        'level TEXT, '
        't_start INT, '
        'task TEXT, '
        'answer TEXT'
        ')'
    )

    return db_connection


def create_user(db_connection, user):
    """
    Функция для добавления нового пользователя в базу данных.
    """
    cursor = db_connection.cursor()
    print(f"Добавить нового пользователя user_id={user['user_id']}: ", end="")
    data = (
        user['user_id'],
        user['category'],
        user['level'],
    )

    try:
        cursor.execute('INSERT INTO Users (user_id, category, level) '
                       'VALUES (?, ?, ?);',
                       data)
        db_connection.commit()
        print(f"Успешно")
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        print("Ошибка")


def update_user(db_connection, user):
    """
    Функция для обновления информации о существующем пользователе.
    """
    cursor = db_connection.cursor()
    print(f"Обновить пользователя user_id={user['user_id']}: ", end="")
    data = (
        user['category'],
        user['level'],
        user['current_task_id'],
        user['user_id'],
    )

    try:
        cursor.execute('UPDATE Users '
                       'SET category = ?, level = ?, current_task_id = ? '
                       'WHERE user_id = ?;',
                       data)
        db_connection.commit()
        print("Успешно")
    except sqlite3.IntegrityError:
        print("Ошибка")


def create_task(db_connection, user):
    """
    Функция для добавления нового запроса в базу данных.
    """
    cursor = db_connection.cursor()
    print(f"Добавить новый запрос user_id={user['user_id']}: ", end="")
    data = (
        user['user_id'],
        user['category'],
        user['level'],
        int(user['t_start']),
        user['task']
    )

    try:
        cursor.execute('INSERT INTO Tasks '
                       '(user_id, category, level, t_start, task) '
                       'VALUES (?, ?, ?, ?, ?);',
                       data)
        db_connection.commit()
        print(f"Успешно, id={cursor.lastrowid}")
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        print("Ошибка")


def update_task(db_connection, user):
    """
    Функция для обновления информации о существующем запросе.
    Для подстраховки проверяем user_id
    """
    cursor = db_connection.cursor()
    print(f"Обновить запрос user_id={user['user_id']}, "
          f"current_task_id={user['current_task_id']}: ", end="")
    data = (
        user['task'],
        user['answer'],
        user['current_task_id'],
        user['user_id']
    )

    try:
        cursor.execute('UPDATE Tasks '
                       'SET task = ?, answer = ? '
                       'WHERE id = ? AND user_id = ?;',
                       data)
        db_connection.commit()
        print("Успешно")
    except sqlite3.IntegrityError:
        print("Ошибка")
