import os
import random
import time

import arrow
import requests
from dotenv import find_dotenv, load_dotenv

TEXT_TEMPLATE = '''
Slot open for *{}* on *{}*!
[Schedule an appointment](https://www.passport.gov.ph/appointment/individual/schedule)
'''.strip()


def bot_get_updates(token):
    resp = requests.post(
        'https://api.telegram.org/bot{}/getUpdates'.format(token))
    print(resp.json())


def bot_send_message(token, chat_id, text):
    resp = requests.post(
        'https://api.telegram.org/bot{}/sendMessage'.format(token),
        data={
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'Markdown',
        })
    if resp.status_code != requests.codes.ok:
        print(resp.content)


def check_site_open(site_id, request_date):
    max_date = '2018-07-01'
    data = {'requestDate': request_date, 'maxDate': max_date,
            'siteId': site_id, 'slots': 1}
    r = requests.post(
        'https://www.passport.gov.ph/appointment/timeslot/available/next',
        headers={
            'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/63.0.3239.132 Safari/537.36'),
        },
        data=data)
    try:
        return r.json()
    except Exception as e:
        print(e, r.content)


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    sites = {
        4: 'Aseana',
        6: 'Megamall',
        7: 'Ali Mall',
    }
    while True:
        for site_id, site_name in sites.items():
            request_date = (arrow.now('Asia/Manila').shift(days=1)
                            .format('YYYY-MM-DD'))
            result = check_site_open(site_id, request_date)
            print(request_date, result)
            if result:
                token = os.getenv('TG_BOT_TOKEN')
                chat_id = os.getenv('TG_BOT_CHAT_ID')
                slot_date = arrow.get(result.get('Date') /
                                      1000).format('YYYY-MM-DD')
                text = TEXT_TEMPLATE.format(site_name, slot_date)
                bot_send_message(token, chat_id, text)
            time.sleep(random.random())
        time.sleep(59 + random.random())

