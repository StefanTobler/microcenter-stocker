import requests
import re
from bs4 import BeautifulSoup
import time
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()
account_sid = os.getenv('TWILIO_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')

phone_to = os.getenv('PHONE_TO')
phone_from = os.getenv('PHONE_FROM')

client = Client(account_sid, auth_token)

SEND = True

def notify(city, product, price, link):
    global SEND
    if SEND:
        message = product + ' is now avaliable at Microcenter ' + city + '! Currently $' + str(price)
        client.api.account.messages.create(
            to=phone_to,
            from_=phone_from,
            body=message + "\n\n" + link)

# Store IDs
# 065 - Duluth
# 041 - Marietta

stores = {
    'Marietta' : '041',
    'Duluth' : '065',
}

targets = {
    '3060' : 0,
    '3070' : 0,
    '3080' : 0,
    #'5000' : 0,
}

while True:
    for city, store in stores.items():
        found = []
        link = 'https://www.microcenter.com/category/4294966937/video-cards?storeid=' + store
        r = requests.get(link)

        soup = BeautifulSoup(r.text, 'html.parser')

        products = soup.find_all(attrs={'class': 'product_wrapper'})

        for product in products:

            product = str(product)
            product = product[product.find('<a class="image"'):]
            product = product[:product.find("/a>")]

            start = re.search('data-name', product).start()
            item = product[start+11:start+100]
            item = item[:item.find('"')]

            price = product.find('data-price') + 12
            price = product[price: price + 12].split('"')[0]

            url = product.find('href') + 6
            url = product[url: url + 256].split('"')[0]
            url = 'https://www.microcenter.com' + url + '?storeid=' + store

            if 'RTX' in item:
                for target, cooldown in targets.items():
                    if target in product and cooldown < 1:
                        print(city, "-", item)
                        notify(city, item, price, url)
                        targets[target] = 30
    time.sleep(60)
    for key in targets.keys():
        if targets[key] > 0:
            targets[key] -= 1
