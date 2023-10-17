import time
import traceback
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import telebot
import requests
from bs4 import BeautifulSoup as bs
import pymongo
from datetime import datetime
import pytz
import threading

myclient = pymongo.MongoClient("mongodb+srv://tsbgalcontract:mymongodb26@cluster0.kppkt.mongodb.net/test")
mydb = myclient["Galcontract"]
auctionscol = mydb["NewRentTelegramAuctions"]
userscol = mydb["NewRentTelegramUsers"]

bot = telebot.TeleBot('5057797542:AAG35Bc4dhBmCFP3FLqsjKstQYmre1iJkS8')


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
                'https://marketplace.prozorro.sale/auction/search?stream=legitimatepropertylease&status=active_rectification&auctionType=priorityenglish')
            soup = bs(page.content, 'html.parser')
            cards = soup.find_all('a', class_='sc-main__title')
            for card in cards:
                href = card.get('href')
                page = requests.get(f'https://marketplace.prozorro.sale{href}')
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
                organizator = procedure_json['relatedOrganizations']['sellingEntity']['name']['uk_UA']
                orendar_list = procedure_json['relatedOrganizations']['currentTenants']
                for orendar in orendar_list:
                    orendar = orendar['name']['uk_UA']
                registry_id = procedure_json['registryId']
                page = requests.get(f'https://procedure.prozorro.sale/api/registry/objects/{registry_id}')
                registry_json = page.json()
                try:
                    orendar_phone = registry_json['relatedOrganizations']['currentTenant']['contactPoint']['telephone']
                except KeyError:
                    orendar_phone = 'Відсутній'
                try:
                    orendar_email = registry_json['relatedOrganizations']['currentTenant']['contactPoint']['email']
                except KeyError:
                    orendar_email = ''
                orendar_code_list = procedure_json['relatedOrganizations']['currentTenants']
                for orendar_code in orendar_code_list:
                    orendar_code = orendar_code['identifier']['id']
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
                            'organizator': organizator, 'orendar': orendar,
                            'orendar_phone': orendar_phone, 'orendar_code': orendar_code, 'address': address,
                            'area': area,
                            'price': price}
                is_present = auctionscol.find_one(document)
                if is_present == None:
                    auctionscol.insert_one(document)
                    for user in userscol.find():
                        bot.send_message(user['tgID'], f'Новий аукціон\n\n'
                                                       f'Дата аукціону: {auction_date}\n'
                                                       f'Посилання: {link}\n'
                                                       f'Організатор: {organizator}\n'
                                                       f'Орендар: {orendar}\n'
                                                       f'Номер телефону: {orendar_phone}\n'
                                                       f'Код орендаря: {orendar_code}\n'
                                                       f"Адреса об'єкту: {address}\n"
                                                       f"Площа: {area}\n"
                                                       f"Ціна: {price}")
                        sender_email = "orenda.tsbgalcontract@gmail.com"
                        if orendar_email == "":
                            receiver_email = "orenda.tsbgalcontract@gmail.com"
                        else:
                            receiver_email = orendar_email
                        password = "eugeyrmaaajakxnj"

                        LotNameEmail = procedure_json["title"]["uk_UA"]
                        LotLinkEmail = f'https://sales.tsbgalcontract.org.ua/auction/{procedure_json["auctionId"]}'
                        LotNumberEmail = procedure_json["auctionId"]

                        message = MIMEMultipart("alternative")
                        message["Subject"] = "Важлива інформація для чинного орендаря"
                        message["From"] = sender_email
                        message["To"] = receiver_email

                        # <span style="font-weight: 400;">Создать текстовую и HTML версию вашего сообщения</span>
                        text = """\
                                                                            HTML NOT AVAILABLE"""

                        htmlEmail = """\
                                                                            <html>
                                                                                <head>
                                                                                </head>
                                                                                    <body style="background-color:rgba(255,253,208,0.5);">
                                                                                    <pre style="font-size:125%;">
                                    Добрий день!

                                    Звертаємо Вашу увагу, що в ЕТС «Прозорро.Продажі» опубліковано аукціон на продовження договору оренди об'єкту <a href="{LotLinkEmail}"> {LotNameEmail} </a> <a href="{LotLinkEmail}"> ({LotNumberEmail}) </a>
                                    Ви є чинним орендарем даних приміщень.
                                    Зареєструватись на участь в електронному аукціоні Ви зможете безкоштовно на електронному майданчику Торгово-сировинної біржі Галконтракт.

                                    Для отримання вичерпної інформацію стосовно процедури продовження Вашого договору оренди зателефонуйте в нашу службу підтримки орендарів (<a href="tel://+380673208517">+380673208517</a>).
                                                                                    </pre>
                                                                                    <hr>
                                                                                    <pre style="font-size:120%;">
                                    З повагою,
                                    ТСБ Галконтракт
                                    p.s. Приносимо вибачення за незручності, якщо Ви отримали даного листа помилково.
                                    <a href="tel://+380673208517">+380673208517</a>
                                    E-mail: info@tsbgalcontract.org.ua
                                    Сайт: tsbgalcontract.org.ua
                                                                                    </pre>
                                                                                    </h3>
                                    <a href="https://www.tsbgalcontract.org.ua/"><img src="https://i.ibb.co/brHpj5W/logo-back.png" width="185" height="90" alt="logo-back" border="0"></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                    <a href="https://t.me/galcontract_bot"><img src="https://i.ibb.co/d2d1FGP/tgemail.png" alt="logo-back" width="600" height="90" border="0" /></a>
                                                                                    </body>
                                                                            </html>
                                                                            """.format(**locals())

                        # Сделать их текстовыми\html объектами MIMEText
                        part1 = MIMEText(text, "plain")
                        part2 = MIMEText(htmlEmail, "html")

                        # Внести HTML\текстовые части сообщения MIMEMultipart
                        # Почтовый клиент сначала попытается отрендерить последнюю часть
                        message.attach(part1)
                        message.attach(part2)

                        # <span style="font-weight: 400;">Создание безопасного подключения с сервером и отправка сообщения</span>
                        context = ssl.create_default_context()
                        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                            server.login(sender_email, password)
                            server.sendmail(
                                sender_email, receiver_email, message.as_string()
                            )

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
