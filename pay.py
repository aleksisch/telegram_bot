from datetime import datetime
from threading import Thread

import requests
import time

def check_pay(message, table):
    cur_time = int(time.time())
    url = "https://edge.qiwi.com/payment-history/v2/persons/{}/payments?rows=50".format(YOUR_QIWI_NUM)
    headers = {'Accept': 'application/json', 'Authorization': "Bearer " + TOKEN_QIWI,
               "Content-Type": "application/json"}
    while time.time() - cur_time < EXPIRED_TIME + 120:
        res = requests.get(url, headers=headers).json()["data"]
        for pay in res:
            if pay['comment'] == str(message.from_user.id):
                if table.check_qiwi_id(pay['txnId']) is True:
                    return
                user = table.get_user(message.from_user.id)
                user.change_balance(int(pay['sum']['amount']), table)
                table.add_qiwi_id(pay['txnId'])
                return
        time.sleep(5)


def get_qiwi_link(message, table):
    time_fmt = "%Y-%m-%dT%H%M"
    to_time = int(time.time()) + EXPIRED_TIME
    expired_time = datetime.fromtimestamp(to_time).strftime(time_fmt)
    url = "https://oplata.qiwi.com/create?publicKey={}&comment={}&lifetime={}" \
        .format(PUBLIC_KEY_QIWI, message.from_user.id, expired_time)
    thread1 = Thread(target=check_pay, args=(message, table))
    thread1.start()
    return url


def get_capusta_link(id):
    url = 'https://api.capusta.space/v1/partner'
    myobj = {
        "id": "uniq_string",
        "amount": {
            "amount": 50 * 100,
            "currency": "RUB"
        },
        "description": id,
        "projectCode": "caller123sbot",
    }
    x = requests.post(url, data=myobj)
    print(x.text)
    return x


if __name__ == "__main__":
    check_pay("1231600379015")
