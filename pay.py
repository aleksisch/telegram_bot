from datetime import datetime
from threading import Thread

import requests
import time
from constants import *
from database import *


def check_pay(message, telegram_bot):
    table = telegram_bot.database
    cur_time = int(time.time())
    url = "https://edge.qiwi.com/payment-history/v2/persons/{}/payments?rows=50".format(YOUR_QIWI_NUM)
    headers = {'Accept': 'application/json', 'Authorization': "Bearer " + TOKEN_QIWI,
               "Content-Type": "application/json"}
    user = table.get_user(message.from_user.id)
    prices = table.get_prices()

    while time.time() - cur_time < EXPIRED_TIME + 120:
        res = requests.get(url, headers=headers).json()["data"]
        #print(res)
        for pay in res:
            if pay['comment'] == str(message.from_user.id) and table.check_qiwi_id(pay['txnId']) is False and pay['status'] == 'SUCCESS':
                amount = int(pay['sum']['amount'])
                for price in prices:
                    if price.amount == amount:
                        table.add_qiwi_id(pay['txnId'])
                        print(price.quantity, user.balance, user.id)
                        user.change_balance(price.quantity, table)
                        telegram_bot.send_message(message.chat.id, Menu.added_to_balance
                                                  .format(price.quantity, user.balance))
                        for admin in ADMIN_ID:
                            telegram_bot.send_message(admin, Menu.admin_added_to_balance.format(user.id, price.quantity, user.balance))
                        break
        time.sleep(5)


def get_qiwi_link(message, btn: PayButton) -> str:
    time_fmt = "%Y-%m-%dT%H%M"
    to_time = int(time.time()) + EXPIRED_TIME
    expired_time = datetime.fromtimestamp(to_time).strftime(time_fmt)
    url = "https://oplata.qiwi.com/create?publicKey={}&amount={}&comment={}&lifetime={}" \
        .format(PUBLIC_KEY_QIWI, btn.amount, message.from_user.id, expired_time)
    return url


if __name__ == "__main__":
    check_pay("1231600379015")
