#!/usr/bin/python3.7
import re
from threading import Thread

import typing
import shutil

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


class Markup:
    @staticmethod
    def get_reply_markup(message, is_add_menu=True):
        markup = types.ReplyKeyboardMarkup(row_width=2)
        if isinstance(message, typing.List):
            for msg in message:
                markup.add(types.KeyboardButton(msg))
        if isinstance(message, str):
            markup.add(types.KeyboardButton(message))
        if is_add_menu is True:
            markup.add(types.KeyboardButton(Menu.main_menu))
        return markup

    @staticmethod
    def inline_song_markup(song):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(Menu.call_this, callback_data=song.id))
        return markup


def decorator_main_menu(func):
    def wrapper(self, msg, *args):
        if msg.text == Menu.main_menu:
            self.set_main_menu(msg)
        else:
            func(self, msg, *args)

    return wrapper


def check_group(text, song_groups):
    for el in song_groups:
        if text == el:
            return True
    return False


def get_category_path(group, category):
    return './{}/{}/{}/'.format(FOLDER_TO_SONG, group, category)


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

        @self.message_handler(func=lambda msg: msg.text == Menu.balance)
        def get_balance(message):
            self.send_message(message.chat.id,
                              "Ваш баланс {}".format(self.database.get_user(message.from_user.id).balance))

        @self.message_handler(func=lambda msg: msg.text == Menu.increase_balance)
        def add_to_balance(message):
            buttons = self.database.get_prices()
            markup = types.InlineKeyboardMarkup()
            for btn in buttons:
                url = get_qiwi_link(message, btn)
                markup.add(types.InlineKeyboardButton(Menu.text_to_pay.format(btn.quantity, btn.amount), url=url))

            thread = Thread(target=check_pay, args=(message, self))
            thread.start()
            self.send_message(message.chat.id, Menu.increase_balance, reply_markup=markup)

        @self.message_handler(func=lambda msg: check_group(msg.text, Menu.song_groups))
        def select_group(msg):
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
            self.send_message(msg.chat.id, Menu.admin_add_to_balance_by_id)
            self.register_next_step_handler(msg, self.admin_add_to_balance1)

        @self.message_handler(func=lambda msg: self.is_from_admin(msg, Menu.admin_send_message_to_all))
        def admin_send_all(msg):
            self.send_message(msg.chat.id, Menu.send_message)
            self.register_next_step_handler(msg, self.admin_send_all1)

        @self.message_handler(func=lambda msg: self.is_from_admin(msg, Menu.admin_add_song))
        def admin_add_song(msg):
            markup = self.get_groups_markup()
            self.send_message(msg.chat.id, Menu.choose_group, reply_markup=markup)
            self.register_next_step_handler(msg, self.add_song1)

        @self.message_handler(func=lambda msg: self.is_from_admin(msg, Menu.admin_delete_category))
        def admin_delete_category(msg):
            self.get_group_category(msg, self.delete_category)

        @self.message_handler(regexp=Menu.all_song)
        def print_all_song(msg):
            songs = self.database.get_all_songs()
            self.send_songs(msg, songs[:PRINT_NUMBER_SONGS])
            self.send_message(msg.chat.id, Menu.get_next_songs.format(PRINT_NUMBER_SONGS),
                              reply_markup=Markup.get_reply_markup(Menu.download))
            self.register_next_step_handler(msg, lambda m: self.get_next_song(m, songs[PRINT_NUMBER_SONGS:]))

    def is_from_admin(self, msg, text):
        return str(msg.from_user.id) == str(self.admin_id) and msg.text == text

    @decorator_main_menu
    def get_group_category(self, msg, callback):
        self.send_message(msg.chat.id, Menu.choose_group, reply_markup=self.get_groups_markup())
        self.register_next_step_handler(msg, lambda m: self.get_category(m, callback))

    @decorator_main_menu
    def get_category(self, msg, callback):
        group_name = msg.text
        markup = Markup.get_reply_markup(self.database.get_category_name(group_name))
        self.send_message(msg.chat.id, Menu.choose_category, reply_markup=markup)
        self.register_next_step_handler(msg, lambda m: self.finish_state(m, group_name, callback))

    @decorator_main_menu
    def finish_state(self, msg, group_name, callback):
        callback(msg, group_name, msg.text)

    @decorator_main_menu
    def admin_send_all1(self, msg):
        users = self.database.get_users()
        for user in users:
            try:
                self.send_message(user.id, msg.text)
            except:
                pass

    @decorator_main_menu
    def get_next_song(self, msg, songs):
        if len(songs) == 0:
            self.send_message(msg.chat.id, Menu.all_songs_printed)
            self.set_main_menu(msg)
        self.send_songs(msg, songs[:PRINT_NUMBER_SONGS])
        self.register_next_step_handler(msg, lambda m: self.get_next_song(m, songs[PRINT_NUMBER_SONGS:]))

    @decorator_main_menu
    def select_category(self, msg, group_name):
        category_name = msg.text
        self.send_songs(msg, self.database.get_songs(group_name, category_name))
        # self.send_message(msg.chat.id, Menu.choose_song, reply_markup=markup)
        # self.register_next_step_handler(msg, self.select_category)

    @decorator_main_menu
    def admin_add_to_balance1(self, msg):
        text = msg.text.split()
        if len(text) == 2 and text[0].isdigit() and text[1].isdigit():
            cur_id = int(text[0])
            num_change = int(text[1])
            user = self.database.get_user(cur_id)
            user.change_balance(num_change, self.database)
            self.send_message(msg.chat.id, Menu.successfull_add)
        self.set_main_menu(msg)

    def set_main_menu(self, message):
        self.send_message(message.chat.id, Menu.main_menu,
                          reply_markup=Markup.get_reply_markup(MENU_BUTTON, False))

    @decorator_main_menu
    def add_song1(self, message):
        markup = Markup.get_reply_markup(self.database.get_category_name(message.text))
        self.send_message(message.chat.id, Menu.choose_category, reply_markup=markup)
        self.register_next_step_handler(message, lambda m: self.add_song2(m, message.text))

    @decorator_main_menu
    def add_song2(self, msg, group_name):
        self.send_message(msg.chat.id, Menu.send_song)
        self.register_next_step_handler(msg, lambda m: self.add_song3(m, group_name, msg.text))

    @decorator_main_menu
    def add_song3(self, message, group_name, category_name):
        if message.content_type == 'audio':
            file_info = self.get_file(message.audio.file_id)
            file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path))
            song_name = message.audio.title
            song_name = song_name

            path = get_category_path(group_name, category_name)
            self.add_path(path)
            with open(path + song_name, 'wb') as f:
                f.write(file.content)
            print(song_name)
            song = Song(group_name, category_name, song_name, message.caption)
            self.database.add_song(song)
            self.send_message(message.chat.id, Menu.successfull_add)
        self.set_main_menu(message)

    def send_songs(self, message, songs):
        for song in songs:
            path = song.get_path()
            audio = open(path, 'rb')
            markup = Markup.inline_song_markup(song)
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

    def add_path(self, path):
        if not os.path.isdir(path):
            os.makedirs(path)

    def get_groups_markup(self):
        groups = self.database.get_groups_name()
        return Markup.get_reply_markup(groups)

    def get_category_markup(self, group):
        category = self.database.get_category_name(group)
        print(category)
        return Markup.get_reply_markup(category)

    @decorator_main_menu
    def print_song(self, msg):
        songs = self.database.get_song_by_name(msg.text)
        self.send_songs(msg, songs)
        # self.register_next_step_handler(msg, self.print_song)

    def delete_category(self, msg, group, category):
        self.database.delete_category(group, category)
        shutil.rmtree(get_category_path(group, category))
        self.set_main_menu(msg)


class ChooseCategory:

    @decorator_main_menu
    def select_category(self, msg, group_name):
        category_name = msg.text
        self.send_songs(msg, self.database.get_songs(group_name, category_name))
        # self.send_message(msg.chat.id, Menu.choose_song, reply_markup=markup)
        # self.register_next_step_handler(msg, self.select_category)


if __name__ == "__main__":
    thread2 = Thread(target=start_server)
    thread2.start()
    bot = TelegramBot()
    bot.start()
