from constants import *

START_HELLO = """Со мной ты сможешь оригинально поздравить родственников, весело подшутить над своими друзьями и жестоко расправиться с врагами 👻

Все очень просто:
1⃣ С помощью меню выбираешь запись розыгрыша.
2⃣ Указываешь номер, на который мне звонить.

При успешном звонке, я пришлю тебе запись разговора, при недозвоне, деньги возвращаются на баланс.

Все операторы 🇺🇦"""

ADD_TO_BALANCE = """У Вас есть шанс получить 1 звонок бесплатно. Подробнее: /freecall
                    Цена звонка: """ + str(PRICE_TO_CALL) + """руб \n 
                    ⚠️ Акция: +30% в подарок от 50 грн (одним платежём)
                    
                    Выберете или напишите сумму пополнения:"""

TO_PAY = """Счёт для оплаты успешно выставлен 😎
            Для пополнения жми на кнопку 👉🏻 'Пополнить'"""

MENU_BUTTON = ["ТОП 10", "Розыгрыши", "Пополнить баланс", "Баланс", "FAQ"]


class Menu:
    top = MENU_BUTTON[0]
    player = MENU_BUTTON[1]
    increase_balance = MENU_BUTTON[2]
    balance = MENU_BUTTON[3]
    faq = MENU_BUTTON[4]
    main_menu = "Главное меню"
    admin = "/admin"
    admin_button = ["/add_song", "/send_to_all", "/get_last_payment", "/add_to_balance_by_id"]
    admin_add_song = admin_button[0]
    admin_send_message_to_all = admin_button[1]
    admin_get_payment = admin_button[2]
    admin_add_to_balance_by_id = "Введите id пользователя и количество звонков, например, \n 243003920 123 \n " \
                                 "увеличит баланс пользователя 243003920 на 123"
    admin_add_to_balance_by_id_cmd = admin_button[3]
    admin_readme = "1. {} - Добавить песню \n 2. {} - послать всем сообщение \n 3. {} - получить последние " \
                   "4. {} - изменить баланс по id" \
                   "оплаченные счета".format(admin_add_song, admin_send_message_to_all, admin_get_payment,
                                             admin_add_to_balance_by_id_cmd)
    choose_group = "Выберите группу"
    send_song = "Пришлите песню и в описании к ней укажите описание"
    qiwi = "Qiwi"
    call_this = "Разыграть"
    enter_number = "Введите номер на который необходимо звонить (например, 79123456789)"
    not_enough_money = "Похоже у вас недостаточно денег"
    making_call = "Совершаем звонок, ожидайте"
    faq_text = "Это faq."
    not_recorded = "Запись не найдена, деньги будут возвращены на ваш счет"
    successfull_add = "Аудиозапись успешно добавлена"
    send_message = "Пришлите сообщение"
    text_to_pay = 'Купить {} звонок за {}'
    default_prices_to_pay = [(1, 35), (3, 99), (10, 249), (100, 1499)]
