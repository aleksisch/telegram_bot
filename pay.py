from datetime import datetime
from threading import Thread

import requests
import time
from constants import *
from database import *


def check_pay(message, table: Table):
    cur_time = int(time.time())
    url = "https://edge.qiwi.com/payment-history/v2/persons/{}/payments?rows=50".format(YOUR_QIWI_NUM)
    headers = {'Accept': 'application/json', 'Authorization': "Bearer " + TOKEN_QIWI,
               "Content-Type": "application/json"}
    while time.time() - cur_time < EXPIRED_TIME + 120:
        res = requests.get(url, headers=headers).json()["data"]
        for pay in res:
            if pay['comment'] == str(message.from_user.id) and table.check_qiwi_id(pay['txnId']) is False:
                user = table.get_user(message.from_user.id)
                prices = table.get_prices()
                amount = int(pay['sum']['amount'])
                for price in prices:
                    if price.amount == amount:
                        user.change_balance(price.quantity, table)
                        table.add_qiwi_id(pay['txnId'])
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
