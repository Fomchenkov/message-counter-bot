#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

import telebot


DB_NAME = 'db.db'
BOT_TOKEN = '418608473:AAE4NnLbjUPx9xIZp-vmUZZZOSwm-c8V4lw'
bot = telebot.TeleBot(BOT_TOKEN)


with sqlite3.connect(DB_NAME) as connection:
    cursor = connection.cursor()
    sql = """CREATE TABLE IF NOT EXISTS users (\
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
        uid INTEGER NOT NULL,\
        uname TEXT NOT NULL,\
        count INTEGER NOT NULL)"""
    cursor.execute(sql)
    connection.commit()


@bot.message_handler(commands=['start'])
def start_command(message):
    text = 'Я бот для подсчета сообщений.'
    return bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['stat'])
def start_command(message):
    """
    Выбрать из базы данных топ сообщений
    """
    cid = message.chat.id
    text = '<b>Топ самых активных участников:</b>\n\n'

    with sqlite3.connect(DB_NAME) as connection:
        cursor = connection.cursor()
        sql = 'SELECT * FROM users ORDER BY count DESC LIMIT 10'
        cursor.execute(sql)
        res = cursor.fetchall()

        i = 1
        for u in res:
            text += '{}. {} - {} сообщений.\n'.format(i, u[2], u[3])
            i += 1

        print(text)

        return bot.send_message(cid, text, parse_mode='html')


@bot.message_handler(content_types=['text'])
def text_photo_handler(message):
    """
    Инкрементировать счетчик сообщений от данного пользователя.
    """
    uid = message.from_user.id
    cid = message.chat.id

    with sqlite3.connect(DB_NAME) as connection:
        cursor = connection.cursor()
        sql = 'SELECT * FROM users WHERE uid=?'
        cursor.execute(sql, (str(uid), ))
        res = cursor.fetchone()
        print(res)
        # Если пользователь есть в базе
        if res:
            count = res[3] + 1
            sql = 'UPDATE users SET count=? WHERE uid=?'
            cursor.execute(sql, (str(count), str(uid))) 
        else:
            uname = '{!s}'.format(message.from_user.first_name)
            if not message.from_user.last_name == None:
                uname += ' {!s}'.format(message.from_user.last_name)
            """
            if not message.from_user.username == None:
                uname += ' (@{!s})'.format(message.from_user.username)
            """
            # Добавить пользователя в базу
            sql = 'INSERT INTO users (uid, uname, count) VALUES (?, ?, ?)'
            cursor.execute(sql, (str(uid), str(uname), str(1)))
        connection.commit()
    return


def main():
    bot.polling(none_stop=True);


if __name__ == '__main__':
    main()
