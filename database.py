# uncompyle6 version 3.5.0
# Python bytecode 3.7 (3394)
# Decompiled from: Python 2.7.5 (default, Aug  7 2019, 00:51:29)
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-39)]
# Embedded file name: /home/aleksey/Freelance/Telegrambot/database.py
# Size of source mod 2**32: 3937 bytes
import os
import sqlite3
from os import listdir
from os.path import isfile, join

from caller_script import *

vox = VoxImplant()


class User:

    def __init__(self, id, balance=0):
        self.id = id
        self.balance = int(balance)

    def add_to_db(self, table):
        table.add_user(self)

    def change_balance(self, new_balance, table):
        self.balance += new_balance
        table.update_user(self)

    def check_for_call(self):
        if self.balance - PRICE_TO_CALL < 0:
            return False
        else:
            return True

    def make_call(self, number, song_id, table):
        vox.call(number,
                 "https://storage-gw-ru-02.voximplant.com/voximplant-records/2020/09/06/MGNlYTU2MjU2NDFkMGQ3YTNmMmQ0NWRmNjY1MzBlYTUvaHR0cDovL3d3dy1ydS0yNy0yMi52b3hpbXBsYW50LmNvbS9yZWNvcmRzLzIwMjAvMDkvMDYvOTE5RDhFQzI2M0E2RjgyNS4xNTk5MzgyMzA1LjExMzMyNjcubXAz?record_id=320274611")
        return True


class Song:

    def __init__(self, group_name, name, number_calls=0, id=0):
        self.group_name = group_name
        self.number_calls = number_calls
        self.name = name
        self.id = id

    def update_calls(self, table):
        table.update_song(self)

    def get_url_by_id(self):
        return 'https://yandex.ru'


class Table:

    def __init__(self, filename='sqlite.db'):
        self.conn = sqlite3.connect(filename, check_same_thread=False)
        self.cursor = self.conn.cursor()
        path = "./{}/".format(FOLDER_TO_SONG)
        all_directory = [x[0] for x in os.walk(path)]
        self.cursor.execute('CREATE TABLE IF NOT EXISTS Groups (group_name text) UNIQUE(group_name)')

        self.cursor.execute('CREATE TABLE IF NOT EXISTS Songs '
                            '(group_name text, song_name text, number_calls int, id int) UNIQUE (group_name, song_name)')

        print('asd')
        for dir in all_directory:
            self.add_group(dir)
            onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]

            for file in onlyfiles:
                song = Song(dir, file)
        print('asd')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS Users (id int, balance int) UNIQUE (id)')

    def add_group(self, name):
        self.cursor.execute('INSERT INTO Groups(group_name) VALUES(?)', (name,))
        self.conn.commit()

    def add_user(self, user: User):
        self.cursor.execute('INSERT INTO Users(id, balance) VALUES(?, ?)', (user.id, user.balance))
        self.conn.commit()

    def add_song(self, song: Song):
        len_song = self.cursor.execute('select count(*) from Songs').fetchall()[0][0]
        song.id = len_song + 1
        self.cursor.execute('INSERT INTO Songs(group_name, song_name, number_calls, id) VALUES(?, ?, ?, ?)', (
            song.group_name, song.name, 0, song.id))
        self.conn.commit()
        return True

    def update_user(self, user: User):
        sql = 'UPDATE Users SET balance = ? WHERE id = ?'
        self.cursor.execute(sql, (user.balance, user.id))
        self.conn.commit()

    def update_song(self, song: Song):
        sql = 'UPDATE Songs SET number_calls = ? WHERE id = ?'
        self.cursor.execute(sql, (song.number_calls, song.id))
        self.conn.commit()

    def get_user(self, id):
        self.cursor.execute('SELECT * FROM Users where id = ?', (id,))
        tmp = self.cursor.fetchall()
        if len(tmp) == 0:
            self.add_user(User(id))
            res = User(id, 0)
        else:
            tmp = tmp[0]
            res = User(tmp[0], tmp[1])
        return res

    def check_group(self, name):
        self.cursor.execute('SELECT * FROM Groups where group_name = ?', (name,))
        tmp = self.cursor.fetchall()
        if len(tmp) == 0:
            return False
        else:
            return True

    def get_groups_name(self):
        self.cursor.execute('SELECT * FROM Groups')
        return [a[0] for a in self.cursor.fetchall()]

    def get_top_song(self, n=PRINT_TOP_N):
        self.cursor.execute('SELECT * FROM Songs ORDER BY number_calls LIMIT ?', (n,))
        return [Song(a[0], a[1], a[2], a[3]) for a in self.cursor.fetchall()]

    def get_song_by_name(self, song_name):
        self.cursor.execute('SELECT * FROM Songs WHERE group_name = ?', (song_name,))
        return [Song(a[0], a[1], a[2], a[3]) for a in self.cursor.fetchall()]


if __name__ == '__main__':
    a = User(1, 1)
    t = Table()
    t.add_group('hello')
    t.add_song(Song('1', '1', 1, '1'))
    t.get_user(1)
    a.change_balance(10, t)
