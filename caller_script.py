#!/usr/bin/python3.7
from datetime import datetime

import pytz
from voximplant.apiclient import VoximplantAPI

from messages import *


class VoxImplant:
    RULE_ID = 3263500
    USER_ID = 7516768

    def __init__(self):
        print("theere")
        self.api = VoximplantAPI("credentials_voximplant.json")

    def call(self, number, url):
        pass
        # self.api.start_scenarios(VoxImplant.RULE_ID, script_custom_data="{} {}".format(number, url),
        #                           user_id=VoxImplant.USER_ID)

    def get_call_record(self, number, message, bot, user, table):
        # time.sleep(120)
        FROM_DATE = datetime(2019, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        TO_DATE = datetime(2050, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        ret = self.api.get_call_history(from_date=FROM_DATE, to_date=TO_DATE,
                                        with_records=True, desc_order=True, count=10)
        res = Menu.not_recorded
        print(ret)
        for item in ret["result"]:
            if item['custom_data'].split()[0] == str(number):
                if len(item["records"]) != 0:
                    res = item["records"][0]["record_url"]
                break
        if res == Menu.not_recorded:
            bot.send_message(message.chat.id, res)
        else:
            bot.send_audio(message.chat.id, res)
            user.change_balance(-5, table)



if __name__ == "__main__":
    vox = VoxImplant()
    print(vox.get_call_record('18005653356'))
