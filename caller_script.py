#!/usr/bin/python3.7
import time
from datetime import datetime

import pytz
from voximplant.apiclient import VoximplantAPI

from messages import *


class VoxImplant:
    RULE_ID = 3270395
    USER_ID = 7782489

    def __init__(self):
        self.api = VoximplantAPI("credentials_voximplant.json")

    def call(self, number, url):
        self.api.start_scenarios(VoxImplant.RULE_ID, script_custom_data="{} {}".format(number, url),
                                 user_id=VoxImplant.USER_ID)

    def get_call_record(self, number, message, bot, user):
        time.sleep(120)
        FROM_DATE = datetime(2019, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        TO_DATE = datetime(2050, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        ret = self.api.get_call_history(from_date=FROM_DATE, to_date=TO_DATE,
                                        with_records=True, desc_order=True, count=10)
        res = Menu.not_recorded
        for item in ret["result"]:
            if len(item['custom_data'].split()) != 0 and item['custom_data'].split()[0] == str(number):
                if len(item["records"]) != 0:
                    res = item["records"][0]["record_url"]
                break
        if res == Menu.not_recorded:
            bot.send_message(message.chat.id, res)
            user.change_balance(PRICE_TO_CALL, bot.database)
        else:
            bot.send_audio(message.chat.id, res)


if __name__ == "__main__":
    vox = VoxImplant()
    print(vox.get_call_record('18005653356'))
