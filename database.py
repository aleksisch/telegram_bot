import sqlite3
import os
from os.path import join
from caller_script import VoxImplant
from constants import *

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
        song = table.get_user(self.id)
        song.add_number_calls(table)
        vox.call(number, "https://{}/{}/{}/{}".format(SERVER_IP, FOLDER_TO_SONG, song.group_name, song.name))
        self.change_balance(-1*PRICE_TO_CALL, table)
        return True


class Song:

    def __init__(self, group_name, name, description, number_calls=0, id=0):
        self.group_name = group_name
        self.number_calls = number_calls
        self.name = name
        self.id = id
        self.description = description

    def update_calls(self, table):
        table.update_song(self)

    def add_number_calls(self, table):
        self.number_calls += 1
        table.update_song(self)


class Table:

    def __init__(self, filename='sqlite.db'):
        self.conn = sqlite3.connect(filename, check_same_thread=False)
        self.cursor = self.conn.cursor()
        path = "./{}/".format(FOLDER_TO_SONG)
        extra_len = 3 + len(FOLDER_TO_SONG)
        all_directory = [x[0] for x in os.walk(path)]
        self.cursor.execute('CREATE TABLE IF NOT EXISTS Groups (group_name text UNIQUE)')

        self.cursor.execute('CREATE TABLE IF NOT EXISTS Songs '
                            '(group_name text, song_name  text, description text, number_calls int, id int, UNIQUE(group_name, song_name))')

        for dir in all_directory:
            dir_name = dir[3 + len(FOLDER_TO_SONG):]
            if len(dir_name) != 0:
                self.add_group(dir[3 + len(FOLDER_TO_SONG):])
                onlyfiles = [f for f in os.listdir(dir) if os.path.isfile(join(dir, f))]
                print(onlyfiles)
                for file in onlyfiles:
                    song = Song(dir[extra_len :], file, "")
                    self.add_song(song)
        self.cursor.execute('CREATE TABLE IF NOT EXISTS Users (id int UNIQUE, balance int)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS QiwiUsedId (id int UNIQUE)')
        self.conn.commit()

    def add_qiwi_id(self, id):
        self.cursor.execute('INSERT OR IGNORE INTO QiwiUsedId(id) VALUES(?)', (id,))
        self.conn.commit()

    def check_qiwi_id(self, id):
        self.cursor.execute('SELECT * FROM QiwiUsedId where id = ?', (id,))
        tmp = self.cursor.fetchall()
        if len(tmp) == 0:
            return False
        else:
            return True


    def add_group(self, name):
        self.cursor.execute('INSERT OR IGNORE INTO Groups(group_name) VALUES(?)', (name,))
        self.conn.commit()

    def add_user(self, user: User):
        self.cursor.execute('INSERT OR IGNORE INTO Users(id, balance) VALUES(?, ?)', (user.id, user.balance))
        self.conn.commit()

    def add_song(self, song: Song):
        len_song = self.cursor.execute('select count(*) from Songs').fetchall()[0][0]
        song.id = len_song + 1
        self.cursor.execute('INSERT OR IGNORE INTO Songs(group_name, song_name, description, number_calls, id) VALUES(?, ?, ?, ?, ?)', (
            song.group_name, song.name, song.description, 0, song.id))
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
        return [Song(a[0], a[1], a[2], a[3], a[4]) for a in self.cursor.fetchall()]

    def get_song_by_name(self, song_name):
        self.cursor.execute('SELECT * FROM Songs WHERE group_name = ?', (song_name,))
        return [Song(a[0], a[1], a[2], a[3], a[4]) for a in self.cursor.fetchall()]

    def get_users(self):
        self.cursor.execute('SELECT * FROM Users')
        return [User(a[0], a[1]) for a in self.cursor.fetchall()]

if __name__ == '__main__':
    a = User(1, 1)
    t = Table()
    t.add_group('hello')
    t.add_song(Song('1', '1', 1, '1'))
    t.get_user(1)
    a.change_balance(10, t)
