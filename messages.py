from constants import *

ADD_TO_BALANCE = """У Вас есть шанс получить 1 звонок бесплатно. Подробнее: /freecall
                    Цена звонка: """ + str(PRICE_TO_CALL) + """руб \n 
                    ⚠️ Акция: +30% в подарок от 50 грн (одним платежём)
                    
                    Выберете или напишите сумму пополнения:"""

TO_PAY = """Счёт для оплаты успешно выставлен 😎
            Для пополнения жми на кнопку 👉🏻 'Пополнить'"""

MENU_BUTTON = ["Топ-10 🏆",
               "Розыгрыши 🎭",
               "Новые 🆕⚡️",
               "Именные 👱🏻‍♂️👩🏻",
               "Праздники 🎉",
               "По объявлениям 📝",
               "Все розыгрыши",
               "Узнать баланс",
               "Пополнить баланс"]


class Menu:
    added_to_balance = "Баланс пополнен на {}. Теперь у вас на счете {} звонков"
    admin_added_to_balance = "Пользователь {} пополнил баланс на {}"
    all_songs_printed = "Все розыгрыши были напечатаны"
    get_next_songs = "Загрузить следующие {}?"
    top = MENU_BUTTON[0]
    song_groups = MENU_BUTTON[1:6]
    all_song = MENU_BUTTON[6]
    balance = MENU_BUTTON[7]
    increase_balance = MENU_BUTTON[8]

    start_msg = """Со мной ты сможешь оригинально поздравить родственников, весело подшутить над своими 
    друзьями и жестоко расправиться с врагами 👻

    Все очень просто:
    1⃣ С помощью меню выбираешь запись розыгрыша.
    2⃣ Указываешь номер, на который мне звонить.

    При успешном звонке, я пришлю тебе запись разговора, при недозвоне, деньги возвращаются на баланс.

    Все операторы 🇺🇦"""
    main_menu = "Главное меню"
    admin = "/admin"
    admin_button = ["/add_song", "/send_to_all", "/get_last_payment", "/add_to_balance_by_id", "/admin_delete_category"]
    admin_add_song = admin_button[0]
    admin_send_message_to_all = admin_button[1]
    admin_get_payment = admin_button[2]
    admin_add_to_balance_by_id = "Введите id пользователя и количество звонков, например, \n 243003920 123 \n " \
                                 "увеличит баланс пользователя 243003920 на 123"
    admin_add_to_balance_by_id_cmd = admin_button[3]
    admin_delete_category = admin_button[4]

    admin_readme = "1. {} - Добавить песню \n " \
                   "2. {} - послать всем сообщение \n " \
                   "3. {} - получить последние оплаченные счета\n" \
                   "4. {} - изменить баланс по id\n" \
                   "5. {} - удалить категорию\n".format(*admin_button)
    choose_group = "Выберите группу"
    choose_category = "Выберите категорию"
    send_song = "Пришлите песню и в описании к ней укажите описание"
    qiwi = "Qiwi"
    call_this = "Разыграть"
    enter_number = "Введите номер на который необходимо звонить (например, 79123456789)"
    not_enough_money = "Похоже у вас недостаточно денег"
    making_call = "Совершаем звонок, ожидайте"
    not_recorded = "Запись не найдена, деньги будут возвращены на ваш счет"
    successfull_add = "Успешно добавлено"
    send_message = "Пришлите сообщение"
    text_to_pay = 'Купить {} звонок за {}руб.'
    default_prices_to_pay = [(1, 35), (3, 99), (10, 249), (100, 1499)]
    download = "Загрузить"
