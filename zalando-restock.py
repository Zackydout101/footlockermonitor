import json
import logging
from time import asctime
import datetime
import time
import requests
from stock_check import check_stocks
import urllib3
import dotenv

CONFIG = dotenv.dotenv_values()
DELAY = CONFIG['DELAY']
INSTOCK = []

s = requests.Session()
res = s.get("https://api.npoint.io/2ae327ce555df178f588")
prod_json = res.json()
product_urls = prod_json

def discord_webhook(product_item):
    data = {}
    data["username"] = CONFIG['USERNAME']
    data["avatar_url"] = CONFIG['AVATAR_URL']
    data["embeds"] = []
    embed = {}
    if product_item == 'initial':
        embed["author"] = {'name': "CONNECTED @ ZALANDO", 'url': 'https://www.zalando.de/',
                           'icon_url': 'https://imgur.com/XzXLEdl.png'}
        embed["description"] = "Cache Cleared Successfully!"
    else:
        embed["author"] = {'name': "UPDATE @ ZALANDO", 'url': 'https://www.zalando.de/',
                           'icon_url': 'https://imgur.com/XzXLEdl.png'}
        embed["title"] = product_item['Title']
        embed["description"] = f"**Price: **\n{product_item['Price']}\n**Stock Status: **\n{product_item['Stock Status']}\n**Sizes: **\n{product_item['Sizes']}"
        embed['url'] = product_item['Url']
        embed['thumbnail'] = {'url': product_item['Image']}

    embed["color"] = int(CONFIG['COLOUR'])
    embed["footer"] = {'text': 'Zalando Monitor',
                       'icon_url': 'https://imgur.com/XzXLEdl.png'}
    embed["timestamp"] = str(datetime.datetime.utcnow())
    data["embeds"].append(embed)

    result = requests.post(CONFIG['WEBHOOK'], data=json.dumps(
        data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        logging.error(msg=err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info("Payload delivered successfully, code {}.".format(
            result.status_code))


def checking_stocks(start):
    try:
        if product_urls:
            instock = check_stocks(product_urls)
            for product in instock:
                print(product)
                if product['Stock Status'] == 'In Stock':
                    if product not in INSTOCK:
                        if(start == 0):
                            discord_webhook(product)
                        INSTOCK.append(product)
                else:
                    if product in INSTOCK:
                        INSTOCK.remove(product)

        time.sleep(float(CONFIG['DELAY']))

    except Exception as e:
        print(str(e))
        time.sleep(float(CONFIG['DELAY']))


def monitor():
    print('STARTING MONITOR')
    logging.info(msg='Successfully started monitor')
    discord_webhook('initial')
    start = 0
    while True:
        print("Starting next cycle")
        checking_stocks(start)
        start = 0


if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()
