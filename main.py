#!/usr/bin/python3.7
import re

import requests
import hashlib
import telebot
from telebot import types
from messages import *
from database import *
from constants import *

bot = telebot.TeleBot(TOKEN, parse_mode=None)
database = Table("sqlite.db")
last_state = 0


def get_reply_markup(mess):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    for msg in mess:
        markup.add(types.KeyboardButton(msg))
    return markup


# def set_song()


def set_main_menu(message):
    bot.send_message(message.chat.id, Menu.main_menu, reply_markup=get_reply_markup([i for i in MENU_BUTTON]))


@bot.message_handler(commands=['start'])
def welcome(message):
    set_main_menu(message)


@bot.message_handler(regexp=Menu.top)
def send_top(message):
    top = database.get_top_song(PRINT_TOP_N)
    top.append(Song("test", "1.mp3", 0, 2342341))
    for item in top:
        print(item)
        audio = open("./{}/{}/{}".format(FOLDER_TO_SONG, item.group_name, item.name), 'rb')
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(Menu.call_this, callback_data=item.id), )
        bot.send_audio(message.chat.id, audio, reply_markup=markup)


@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and message.text == Menu.admin_add_song)
def add_song(message):
    a = database.get_groups_name()
    groups = [i[0] for i in a]
    bot.send_message(message.chat.id, Menu.choose_group, reply_markup=get_reply_markup(groups))
    bot.register_next_step_handler(message, add_song1)


def add_song1(message):
    if database.check_group(message.text) is True or 1:
        bot.send_message(message.chat.id, Menu.send_song)
        bot.register_next_step_handler(message, lambda m: add_song2(m, message.text))
    else:
        set_main_menu(message)


def add_song2(message, group_name):
    if message.content_type == 'audio':
        file_info = bot.get_file(message.audio.file_id)
        file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path))
        song_name = message.audio.title
        path = './songs/{0}/{1}'.format(group_name, song_name)
        with open(path, 'wb') as f:
            f.write(file.content)
        song = Song(group_name, song_name)
        database.add_song(song)
    else:
        set_main_menu(message)


@bot.message_handler(func=lambda message: message.text == Menu.balance)
def get_balance(message):
    bot.send_message(message.chat.id, "Ваш баланс {}".format(database.get_user(message.from_user.id).balance))


@bot.message_handler(func=lambda message: message.text == Menu.increase_balance)
def add_to_balance(message):
    url = "https://www.free-kassa.ru/merchant/cash.php?m={}&oa={}&o={}&s={}".format(FREE_CASSA_ID, 100,
                                                                                    message.from_user.id, hashlib.md5(
            "{}:{}:{}:{}".format(FREE_CASSA_ID, 100, SECRET_KEY, ADMIN_ID).encode()).hexdigest())
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(Menu.free_cassa, url=url))
    bot.send_message(message.chat.id, Menu.increase_balance, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.message.audio is not None)
def get_number_to_call(call):
    user = database.get_user(call.from_user.id)
    if user.check_for_call() is True:
        bot.send_message(call.message.chat.id, Menu.enter_number)
        bot.register_next_step_handler(call.message, lambda m: make_call(m, call.data))
    else:
        bot.send_message(call.message.chat.id, Menu.not_enough_money)
        add_to_balance(call.message)


def make_call(message, song_id):
    pattern = re.compile(r'^(?:\+|00)?(\d+)$')
    number = pattern.search(message.text)
    if number is not None:
        number = number.group(1)
        user = database.get_user(message.from_user.id)
        user.make_call(number, song_id, database)
        bot.send_message(message.chat.id, Menu.making_call)
    else:
        set_main_menu(message)


@bot.message_handler(regexp=Menu.faq)
def print_faq(message):
    bot.send_message(message.chat.id, Menu.faq_text)


@bot.message_handler(regexp=Menu.player)
def choose_song(message):
    bot.send_message(message.chat.id, Menu.faq_text)


if __name__ == "__main__":
    bot.polling()
