#!/usr/bin/python3.7
import re
from threading import Thread
from caller_script import *
import requests
import hashlib
import telebot
from telebot import (types,
                     TeleBot)
from messages import *
from database import *
from constants import *
import constants
from pay import *
from server import start_server


def get_reply_markup(mess):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    for msg in mess:
        markup.add(types.KeyboardButton(msg))
    markup.add(types.KeyboardButton(Menu.main_menu))
    return markup


def decorator_main_menu(func):
    def wrapper(self, msg):
        if msg.text == Menu.main_menu:
            self.set_main_menu(msg)
        else:
            func(self, msg)

    return wrapper


def check_group(text, song_groups):
    for el in song_groups:
        if text == el:
            return True
    return False


class TelegramBot(TeleBot):

    def start(self):
        self.polling()

    def __init__(self):
        super().__init__(TOKEN, parse_mode=None)
        self.database = Table(constants.database_name)
        self.admin_id = self.database.get_admin_id()
        self.vox = VoxImplant()

        @self.message_handler(regexp=Menu.main_menu)
        def send_top(message):
            self.set_main_menu(message)

        @self.message_handler(commands=['admin'])
        def admin_commands(msg):
            self.send_message(msg.chat.id, Menu.admin_readme)

        @self.message_handler(commands=['start'])
        def welcome(message):
            self.send_message(message.chat.id, self.database.get_start_msg())
            self.set_main_menu(message)

        @self.message_handler(regexp=Menu.top)
        def send_top(message):
            top = self.database.get_top_song(PRINT_TOP_N)
            self.send_songs(message, top)

        @self.message_handler(regexp=Menu.player)
        def select_group(message):
            markup = self.get_groups_markup()
            self.send_message(message.chat.id, Menu.choose_group, reply_markup=markup)
            self.register_next_step_handler(message, self.print_song)

        # @self.message_handler(func=lambda msg: msg.text == Menu.balance)
        # def get_balance(message):
        #     self.send_message(message.chat.id,
        #                       "Ваш баланс {}".format(self.database.get_user(message.from_user.id).balance))

        @self.message_handler(func=lambda msg: msg.text == Menu.increase_balance)
        def add_to_balance(message):
            buttons = self.database.get_prices()
            markup = types.InlineKeyboardMarkup()
            for btn in buttons:
                url = get_qiwi_link(message, btn)
                markup.add(types.InlineKeyboardButton(Menu.text_to_pay.format(btn.quantity, btn.amount), url=url))

            thread = Thread(target=check_pay, args=(message, self.database))
            thread.start()
            self.send_message(message.chat.id, Menu.increase_balance, reply_markup=markup)

        @self.message_handler(func=lambda msg: check_group(msg.text, Menu.song_groups))
        def select_group(msg):
            self.send_message(msg.chat.id, Menu.choose_category)
            group_name = msg.text
            markup = self.get_category_markup(group_name)
            self.send_message(msg.chat.id, Menu.choose_category, reply_markup=markup)
            self.register_next_step_handler(msg, lambda m: self.select_category(m, group_name))

        @self.callback_query_handler(func=lambda call: call.message.audio is not None)
        def get_number_to_call(call):
            user = self.database.get_user(call.from_user.id)
            if user.check_for_call() is True:
                self.send_message(call.message.chat.id, Menu.enter_number)
                self.register_next_step_handler(call.message, lambda m: self.make_call(m, call.data))
            else:
                self.send_message(call.message.chat.id, Menu.not_enough_money)
                add_to_balance(call.message)

        @self.message_handler(func=lambda msg: self.is_from_admin(msg, Menu.admin_add_to_balance_by_id_cmd))
        def admin_add_to_balance(msg):
            print("here")
            self.send_message(msg.chat.id, Menu.admin_add_to_balance_by_id)
            self.register_next_step_handler(msg, self.admin_add_to_balance1)

        @self.message_handler(func=lambda msg: self.is_from_admin(msg, Menu.admin_add_song))
        @decorator_main_menu
        def add_song(msg):
            markup = msg.get_groups_markup()
            self.send_message(msg.chat.id, Menu.choose_group, reply_markup=markup)
            self.register_next_step_handler(msg, self.add_song1)

    def is_from_admin(self, msg, text):
        return str(msg.from_user.id) == str(self.admin_id) and msg.text == text

    @decorator_main_menu
    def select_category(self, msg, group_name):
        category_name = msg.text
        self.send_songs(msg, self.database.get_songs(group_name, category_name))
        # self.send_message(msg.chat.id, Menu.choose_song, reply_markup=markup)
        # self.register_next_step_handler(msg, self.select_category)

    @decorator_main_menu
    def admin_add_to_balance1(self, msg):
        text = msg.text.split()
        cur_id = int(text[0])
        num_change = int(text[1])
        user = self.database.get_user(cur_id)
        user.change_balance(num_change, self.database)
        self.send_message(msg.chat.id, Menu.successfull_add)
        self.set_main_menu(msg)

    def set_main_menu(self, message):
        self.send_message(message.chat.id, Menu.main_menu, reply_markup=get_reply_markup([i for i in MENU_BUTTON]))

    def add_song1(self, message):
        self.send_message(message.chat.id, Menu.send_song)
        self.register_next_step_handler(message, lambda m: self.add_song2(m, message.text))

    def add_song2(self, message, group_name):
        if message.content_type == 'audio':
            file_info = self.get_file(message.audio.file_id)
            file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path))
            song_name = message.audio.title
            song_name = song_name.encode('cp1252')
            path = './{}/{}/{}'.format(FOLDER_TO_SONG, group_name, song_name)
            self.add_path(group_name)
            with open(path, 'wb') as f:
                f.write(file.content)
            print(song_name)
            song = Song(group_name, song_name, message.caption)
            self.database.add_song(song)
            self.send_message(message.chat.id, Menu.successfull_add)
        self.set_main_menu(message)

    def send_songs(self, message, songs):
        for song in songs:
            path = "./{}/{}/{}".format(FOLDER_TO_SONG, song.group_name, song.name)
            audio = open(path, 'rb')
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(Menu.call_this, callback_data=song.id))
            self.send_audio(message.chat.id, caption=song.description, audio=audio, reply_markup=markup)

    def make_call(self, message, song_id):
        pattern = re.compile(r'^(?:\+|00)?(\d+)$')
        number = pattern.search(message.text)
        if number is not None:
            number = number.group(1)
            user = self.database.get_user(message.from_user.id)
            user.make_call(number, song_id, self.database)
            self.send_message(message.chat.id, Menu.making_call)
            thread1 = Thread(target=self.vox.get_call_record, args=(number, message, self, user))
            thread1.start()
        else:
            self.set_main_menu(message)

    def add_path(self, name):
        path = './{}/{}'.format(FOLDER_TO_SONG, name)
        try:
            os.mkdir(path)
        except:
            pass
        self.database.add_group(name)

    def get_groups_markup(self):
        groups = self.database.get_groups_name()
        return get_reply_markup(groups)

    def get_category_markup(self, group):
        category = self.database.get_category_name(group)
        return get_reply_markup(category)

    @decorator_main_menu
    def print_song(self, msg):
        songs = self.database.get_song_by_name(msg.text)
        self.send_songs(msg, songs)
        # self.register_next_step_handler(msg, self.print_song)


if __name__ == "__main__":
    thread2 = Thread(target=start_server)
    thread2.start()
    bot = TelegramBot()
    bot.start()
