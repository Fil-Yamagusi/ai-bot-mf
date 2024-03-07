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


def get_stat(db_connection, type):
    """
    Разная статистика. Одна функция с параметром
    """
    cursor = db_connection.cursor()

    # Простая инфа про пользователей
    if type == 'users':
        ds = {}
        try:
            total = 0

            # print("Количество пользователей и разбиение по уровням")
            q = ("SELECT COUNT(*) as amount, level "
                 "FROM Users group by level")
            cursor.execute(q)
            res = cursor.fetchall()
            # print(f"{res=}")

            ds['levels'] = {}
            for r in res:
                total += r[0]
                ds['levels'][r[1]] = r[0]
            ds['total'] = total

            # print("Топ-3 пользователей по запросам")
            q = ("SELECT COUNT(*) as amount, user_id "
                 "FROM Tasks group by user_id ORDER BY amount DESC LIMIT 3")
            cursor.execute(q)
            res = cursor.fetchall()
            # print(f"{res=}")

            ds['uids'] = {}
            for r in res:
                ds['uids'][r[1]] = r[0]

            # print("Успешно")

        except sqlite3.IntegrityError:
            print("Ошибка users")

        return ds

    # Простая инфа про запросы
    if type == 'tasks':
        ds = {}
        try:
            total = 0

            # print("Количество запросов и разбиение по уровням")
            q = ("SELECT COUNT(*) as amount, level "
                 "FROM Tasks group by level")
            cursor.execute(q)
            res = cursor.fetchall()
            # print(f"{res=}")

            ds['levels'] = {}
            for r in res:
                total += r[0]
                ds['levels'][r[1]] = r[0]
            ds['total'] = total

            # print("Количество запросов и разбиение по категориям")
            q = ("SELECT COUNT(*) as amount, category "
                 "FROM Tasks group by category")
            cursor.execute(q)
            res = cursor.fetchall()
            # print(f"{res=}")

            ds['category'] = {}
            for r in res:
                ds['category'][r[1]] = r[0]

            # print("Количество запросов по часам в течение дня")
            q = ("SELECT count(user_id) as amount, "
                 "strftime('%H', datetime(t_start, 'unixepoch', 'localtime')) "
                 "as H "
                 "FROM Tasks GROUP BY H ORDER BY H ASC")
            cursor.execute(q)
            res = cursor.fetchall()
            # print(f"{res=}")

            data_src = [f"{i:02}" for i in range(0, 24)]
            ds['hour'] = {}
            for d in data_src:
                ds['hour'][d] = 0
            for r in res:
                ds['hour'][r[1]] = r[0]

            # print("Успешно")

        except sqlite3.IntegrityError:
            print("Ошибка tasks")

        return ds
