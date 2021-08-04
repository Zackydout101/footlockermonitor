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

product_urls = [
    'https://superkicks.in/product/cl-legacy-chalk-blue-2/',
    ' https://superkicks.in/product/jurassic-park-stomper/'
]


def discord_webhook(product_item):
    data = {}
    data["username"] = CONFIG['USERNAME']
    data["avatar_url"] = CONFIG['AVATAR_URL']
    data["embeds"] = []
    embed = {}
    if product_item == 'initial':
        embed["author"] = {'name': "CONNECTED @ SK RESTOCK", 'url': 'https://www.vegnonveg.com/',
                           'icon_url': 'https://i.ytimg.com/vi/UumOWHyCMBM/hqdefault.jpg'}
        embed["description"] = "Cache Cleared Successfully!"
    else:
        embed["author"] = {'name': "RESTOCK @ SK", 'url': 'https://www.vegnonveg.com/',
                           'icon_url': 'https://i.ytimg.com/vi/UumOWHyCMBM/hqdefault.jpg'}
        embed["title"] = product_item['Title']
        embed["description"] = f"**Price: **{product_item['Price']}\n**Stock Status: **{product_item['Stock Status']}\n**Sizes Available: **{product_item['Sizes']}"
        embed['url'] = product_item['Url']
        embed['thumbnail'] = {'url': product_item['Image']}

    embed["color"] = int(CONFIG['COLOUR'])
    embed["footer"] = {'text': 'SK Monitor',
                       'icon_url': 'https://i.ytimg.com/vi/UumOWHyCMBM/hqdefault.jpg'}
    embed["fields"] = [{'name': 'Quick Links: ', 'value': '[StockX](https://www.stockx.com)' + ' | ' + '[Goat](https://www.goat.com)' +
                        ' | ' + '[eBay](https://www.ebay.com/)', 'inline': True}]
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
    start = 1
    while True:
        print("Starting next cycle")
        checking_stocks(start)
        start = 0


if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()
