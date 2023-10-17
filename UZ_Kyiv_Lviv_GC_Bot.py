import time
import traceback
import telebot
import requests
from bs4 import BeautifulSoup as bs
import pymongo
from datetime import datetime
import pytz
import threading

myclient = pymongo.MongoClient("mongodb+srv://tsbgalcontract:mymongodb26@cluster0.kppkt.mongodb.net/test")
mydb = myclient["Galcontract"]
auctionscol = mydb["UzKyivLvivAuctions"]
userscol = mydb["UzKyivLvivUsers"]

bot = telebot.TeleBot('6303442001:AAGr3vWg0uG2wgNAdxzn9xEphgPM0ruIM4Q')


def run():
    def Bot():
        @bot.message_handler(commands=['start'])
        def start(message):
            document = {'tgID': message.from_user.id}
            is_present = userscol.find_one(document)
            if is_present is None:
                userscol.insert_one(document)
            bot.send_message(message.from_user.id, 'Вас успішно зареєстровано')

        bot.polling(none_stop=True)

    def Main():
        def SubMain():
            page = requests.get(
                'https://prozorro.sale/auction/?stream=sellout&stream=otherassets&stream=legitimatepropertylease&stream=propertylease&stream=alienation&edrpou=40075815&item_region=%D0%9A%D0%B8%D1%97%D0%B2&item_region=%D0%9A%D0%B8%D1%97%D0%B2%D1%81%D1%8C%D0%BA%D0%B0+%D0%BE%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C&item_region=%D0%9B%D1%8C%D0%B2%D1%96%D0%B2%D1%81%D1%8C%D0%BA%D0%B0+%D0%BE%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C&classifier_id=04000000-8&status=active_tendering&status=active_rectification&size=50')
            soup = bs(page.content, 'html.parser')
            cards = soup.find_all('a', class_='sc-main__title')
            for card in cards:
                href = card.get('href')
                page = requests.get(f'https://prozorro.sale{href}')
                soup = bs(page.content, 'html.parser')
                hashID_div = soup.find('div', class_='information-id-and-num__id')
                hashID = hashID_div.find_all('span')[1].text[27:]
                page = requests.get(f'https://procedure.prozorro.sale/api/procedures/{hashID}')
                procedure_json = page.json()
                auction_date_string = procedure_json['auctionPeriod']['startDate']
                dt_obj = datetime.strptime(auction_date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
                gmt3 = pytz.timezone('Europe/Kiev')
                dt_gmt3 = dt_obj.replace(tzinfo=pytz.utc).astimezone(gmt3)
                auction_date = dt_gmt3.strftime('%d.%m.%Y %H:%M')
                link = f'https://sales.tsbgalcontract.org.ua/auction/{procedure_json["auctionId"]}'
                organizator = 'АКЦІОНЕРНЕ ТОВАРИСТВО "УКРАЇНСЬКА ЗАЛІЗНИЦЯ"'
                address = f"{procedure_json['items'][0]['address']['region']['uk_UA']}, {procedure_json['items'][0]['address']['locality']['uk_UA']}, {procedure_json['items'][0]['address']['streetAddress']['uk_UA']}"
                try:
                    area = procedure_json['items'][0]['reProps']['totalObjectArea']
                except KeyError:
                    area = 'Не вказано'
                tax = procedure_json['value']['valueAddedTaxIncluded']
                if tax is True:
                    price = f"{procedure_json['value']['amount']} з ПДВ"
                elif tax is False:
                    price = f"{procedure_json['value']['amount']} без ПДВ"
                document = {'auction_date': auction_date, 'auctionID': procedure_json["auctionId"],
                            'organizator': organizator, 'address': address, 'area': area,
                            'price': price}
                is_present = auctionscol.find_one(document)
                if is_present == None:
                    auctionscol.insert_one(document)
                    for user in userscol.find():
                        bot.send_message(user['tgID'], f'Новий аукціон\n\n'
                                                       f'Дата аукціону: {auction_date}\n'
                                                       f'Посилання: {link}\n'
                                                       f'Організатор: {organizator}\n'
                                                       f"Адреса об'єкту: {address}\n"
                                                       f"Площа: {area}\n"
                                                       f"Ціна: {price}")

        while True:
            try:
                SubMain()
                time.sleep(60)
            except Exception as e:
                bot.send_message(155840708, str(e))
                print(traceback.format_exc())

    if __name__ == '__main__':
        t1 = threading.Thread(target=Bot)
        t2 = threading.Thread(target=Main)
        t1.start()
        t2.start()
