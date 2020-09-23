import sqlite3
import os
from os.path import join
from caller_script import VoxImplant
from constants import *
from messages import Menu
import urllib.request
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
        song = table.get_song(song_id)
        song.add_number_calls(table)
        tmp = urllib.request.pathname2url
        url = "http://{}/{}/{}/{}".format(SERVER_IP, tmp(FOLDER_TO_SONG), tmp(song.group_name), tmp(song.name))
        print(url)
        vox.call(number, url)
        self.change_balance(-1, table)
        return True

    def get_tuple(self):
        return self.balance, self.id


class Song:

    def __init__(self, group_name, category_name, name, description = "", number_calls=0, id=0):
        self.group_name = group_name
        self.category_name = category_name
        self.number_calls = number_calls
        self.name = name
        self.id = id
        self.description = description

    def update_calls(self, table):
        table.update_song(self)

    def add_number_calls(self, table):
        self.number_calls += 1
        table.update_song(self)

    def get_tuple(self):
        return (self.group_name,
                self.category_name,
                self.name,
                self.description,
                self.number_calls,
                self.id)

    def get_path(self):
        return "./{}/{}/{}/{}".format(FOLDER_TO_SONG, self.group_name, self.category_name, self.name)

    def remove_song(self, table):
        os.remove(self.get_path())
        table.remove_song(self.id)


class PayButton:

    def __init__(self, quantity:int, amount:int):
        self.amount = amount
        self.quantity = quantity

class Table:

    def __init__(self, filename='sqlite.db'):
        self.conn = sqlite3.connect(filename, check_same_thread=False)
        self.cursor = self.conn.cursor()
        path = "./{}/".format(FOLDER_TO_SONG)
        extra_len = 3 + len(FOLDER_TO_SONG)

        self.cursor.execute('DROP TABLE IF EXISTS Songs')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS Songs '
                            '(group_name text, category_name text, song_name  text, description text,'
                            ' number_calls int, id int, UNIQUE(group_name, category_name, song_name))')

        only_folder = [f for f in os.listdir(path) if not os.path.isfile(join(path, f))]
        for group in only_folder:
            path1 = path + group + '/'
            all_category = [f for f in os.listdir(path1) if not os.path.isfile(join(path1, f))]
            for category in all_category:
                path2 = path1 + category + '/'
                files = [f for f in os.listdir(path2) if os.path.isfile(join(path2, f))]
                for file in files:
                    print(group, category, file)
                    song = Song(group, category, file, "")
                    self.add_song(song)
        self.cursor.execute('CREATE TABLE IF NOT EXISTS Users (id int UNIQUE, balance int)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS QiwiUsedId (id int UNIQUE)')
        self.conn.commit()

    def add_qiwi_id(self, id):
        self.cursor.execute('INSERT OR IGNORE INTO QiwiUsedId(id) VALUES(?)', (id,))
        self.conn.commit()

    def check_qiwi_id(self, id):
        self.cursor.execute("SELECT * FROM QiwiUsedId where id = ?", (id,))
        tmp = self.cursor.fetchall()
        if len(tmp) == 0:
            return False
        else:
            return True


    def add_user(self, user: User):
        self.cursor.execute('INSERT OR IGNORE INTO Users(id, balance) VALUES(?, ?)', (user.id, user.balance))
        self.conn.commit()

    def add_song(self, song: Song):
        len_song = self.cursor.execute('select count(*) from Songs').fetchall()[0][0]
        song.id = len_song + 1
        self.cursor.execute('INSERT OR IGNORE INTO Songs(group_name, category_name, song_name, description,'
                            ' number_calls, id) VALUES(?, ?, ?, ?, ?, ?)', song.get_tuple())
        self.conn.commit()
        return True

    def update_user(self, user: User):
        sql = 'UPDATE Users SET balance = ? WHERE id = ?'
        self.cursor.execute(sql, user.get_tuple())
        self.conn.commit()

    def update_song(self, song: Song):
        sql = 'UPDATE Songs SET number_calls = ? WHERE id = ?'
        self.cursor.execute(sql, (song.number_calls, song.id))
        self.conn.commit()

    def get_user(self, id) -> User:
        self.cursor.execute('SELECT * FROM Users where id = ?', (id,))
        tmp = self.cursor.fetchall()
        if len(tmp) == 0:
            self.add_user(User(id))
            res = User(id, 0)
        else:
            tmp = tmp[0]
            res = User(tmp[0], tmp[1])
        return res

    def get_groups_name(self) -> List[str]:
        self.cursor.execute('SELECT DISTINCT group_name FROM Songs')
        return [item[0] for item in self.cursor.fetchall()]

    def get_category_name(self, group_name: str):
        self.cursor.execute('SELECT DISTINCT category_name FROM Songs where group_name = ?', (group_name,))
        return [item[0] for item in self.cursor.fetchall()]

    def get_top_song(self, n=PRINT_TOP_N) -> List[Song]:
        self.cursor.execute('SELECT * FROM Songs ORDER BY number_calls LIMIT ?', (n,))
        return [Song(*item) for item in self.cursor.fetchall()]

    def get_all_songs(self) -> List[Song]:
        self.cursor.execute('SELECT * FROM Songs ORDER BY number_calls')
        return [Song(*item) for item in self.cursor.fetchall()]

    def get_song_by_name(self, song_name) -> List[Song]:
        self.cursor.execute('SELECT * FROM Songs WHERE group_name = ?', (song_name,))
        return [Song(*item) for item in self.cursor.fetchall()]

    def get_song(self, id) -> Song:
        self.cursor.execute('SELECT * FROM Songs WHERE id = ?', (id,))
        return [Song(*item) for item in self.cursor.fetchall()][0]

    def get_users(self) -> List[User]:
        self.cursor.execute('SELECT * FROM Users')
        return [User(*item) for item in self.cursor.fetchall()]

    def get_prices(self) -> List[PayButton]:
        """return list of buttons where buttons[i][0] - number of calls, numbers[i][1] price for this number"""
        return [PayButton(*item) for item in Menu.default_prices_to_pay]

    def get_admin_id(self) -> int:
        return ADMIN_ID

    def get_start_msg(self) ->str:
        return Menu.start_msg

    def get_songs(self, group: str, category: str) -> List[Song]:
        self.cursor.execute('SELECT * FROM Songs WHERE group_name = ? and category_name = ?', (group, category))
        return [Song(*item) for item in self.cursor.fetchall()]

    def remove_song(self, id):
        sql = 'DELETE FROM Songs WHERE id = ?'
        self.cursor.execute(sql, (id,))
        self.conn.commit()


if __name__ == '__main__':
    a = User(1, 1)
    t = Table()
    t.add_group('hello')
    t.add_song(Song('1', '1', 1, '1'))
    t.get_user(1)
    a.change_balance(10, t)
