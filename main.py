#!/usr/bin/python3.7
import re
from threading import Thread
from caller_script import *
import requests
import hashlib
import telebot
from telebot import (types, TeleBot)
from messages import *
from database import *
from constants import *
import constants
from pay import *
from server import start_server

bot = telebot.TeleBot(TOKEN, parse_mode=None)
database = Table("sqlite.db")


class TelegramBot(TeleBot):

    def __init__(self):
        super().__init__(self, TOKEN, parse_mode=None)
        self.database = Table(constants.database_name)

    @TeleBot.message_handler(regexp=Menu.main_menu)
    def send_top(self, message):
        set_main_menu(message)

def add_path(name):
    path = './{}/{}'.format(FOLDER_TO_SONG, name)
    try:
        os.mkdir(path)
    except:
        pass
    database.add_group(name)


def get_reply_markup(mess):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    for msg in mess:
        markup.add(types.KeyboardButton(msg))
    markup.add(types.KeyboardButton(Menu.main_menu))
    return markup


def get_groups_markup():
    groups = database.get_groups_name()
    return get_reply_markup(groups)


def send_songs(message, songs):
    for song in songs:
        path = "./{}/{}/{}".format(FOLDER_TO_SONG, song.group_name, song.name)
        audio = open(path, 'rb')
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(Menu.call_this, callback_data=song.id))
        bot.send_audio(message.chat.id, caption=song.description, audio=audio, reply_markup=markup)


# def set_song()


def set_main_menu(message):
    bot.send_message(message.chat.id, Menu.main_menu, reply_markup=get_reply_markup([i for i in MENU_BUTTON]))


@bot.message_handler(commands=['admin'])
def admin_commands(msg):
    bot.send_message(msg.chat.id, Menu.admin_readme)


@bot.message_handler(commands=['start'])
def welcome(message):
    set_main_menu(message)


@bot.message_handler(regexp=Menu.top)
def send_top(message):
    top = database.get_top_song(PRINT_TOP_N)
    send_songs(message, top)


@bot.message_handler(
    func=lambda message: message.from_user.id == ADMIN_ID and message.text == Menu.admin_send_message_to_all)
def send_message(message):
    bot.send_message(message.chat.id, Menu.send_message)
    bot.register_next_step_handler(message, send_message1)

@bot.message_handler(
    func=lambda message: message.from_user.id == ADMIN_ID and message.text == Menu.admin_add_to_balance_by_id_cmd)
def change_balance():


def send_message1(message):
    users = database.get_users()
    for user in users:
        try:
            bot.send_message(user.id, message.text)
        except:
            pass


@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and message.text == Menu.admin_add_song)
def add_song(message):
    markup = get_groups_markup()
    bot.send_message(message.chat.id, Menu.choose_group, reply_markup=markup)
    bot.register_next_step_handler(message, add_song1)


@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and message.text == Menu.admin_add_song)
def add_song(message):
    if message.text == Menu.main_menu:
        set_main_menu()
        return
    markup = get_groups_markup()
    bot.send_message(message.chat.id, Menu.choose_group, reply_markup=markup)
    bot.register_next_step_handler(message, add_song1)


def add_song1(message):
    bot.send_message(message.chat.id, Menu.send_song)
    bot.register_next_step_handler(message, lambda m: add_song2(m, message.text))


def add_song2(message, group_name):
    if message.content_type == 'audio':
        file_info = bot.get_file(message.audio.file_id)
        file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path))
        song_name = message.audio.title
        song_name = song_name.encode('cp1252')
        path = './{}/{}/{}'.format(FOLDER_TO_SONG, group_name, song_name)
        add_path(group_name)
        with open(path, 'wb') as f:
            f.write(file.content)
        print(song_name)
        song = Song(group_name, song_name, message.caption)
        database.add_song(song)
        bot.send_message(message.chat.id, Menu.successfull_add)
    set_main_menu(message)


@bot.message_handler(func=lambda message: message.text == Menu.balance)
def get_balance(message):
    bot.send_message(message.chat.id, "Ваш баланс {}".format(database.get_user(message.from_user.id).balance))


@bot.message_handler(func=lambda message: message.text == Menu.increase_balance)
def add_to_balance(message):
    buttons = database.get_prices()
    markup = types.InlineKeyboardMarkup()
    for btn in buttons:
        url = get_qiwi_link(message, btn)
        markup.add(types.InlineKeyboardButton(Menu.text_to_pay.format(btn.quantity, btn.amount), url=url))

    thread = Thread(target=check_pay, args=(message, database))
    thread.start()
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
        thread1 = Thread(target=vox.get_call_record, args=(number, message, bot, user, database))
        thread1.start()
    else:
        set_main_menu(message)


@bot.message_handler(regexp=Menu.faq)
def print_faq(message):
    bot.send_message(message.chat.id, Menu.faq_text)


@bot.message_handler(regexp=Menu.player)
def choose_group(message):
    markup = get_groups_markup()
    bot.send_message(message.chat.id, Menu.choose_group, reply_markup=markup)
    bot.register_next_step_handler(message, print_song)


def print_song(message):
    if message.text == Menu.main_menu:
        set_main_menu(message)
    else:
        songs = database.get_song_by_name(message.text)
        send_songs(message, songs)
        bot.register_next_step_handler(message, print_song)


if __name__ == "__main__":
    thread2 = Thread(target=start_server)
    thread2.start()
    bot.polling()
