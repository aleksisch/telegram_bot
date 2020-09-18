from constants import *
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
        self.change_balance(-1 * PRICE_TO_CALL, table)
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
