import traceback
import telebot
import requests
import schedule
import time
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from lxml import html
import pymongo
from datetime import datetime

bot = telebot.TeleBot('5705698943:AAENU1pSWZ2n1O8zmtIx1CHa4Oepl5TF-do')


def run():
    def ObjectsOfRent():
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
            "Accept-Encoding": "*",
            "Connection": "keep-alive"
        }
        page = requests.get(
            "https://old.prozorro.sale/registries/search?source=lease&status=sold&listType=First&listType=Undefined&offset=10&item_region=43%E2%80%9345&item_region=88%E2%80%9390&item_region=79%E2%80%9382",
            headers=headers)
        tree = html.fromstring(page.content)
        hrefs = tree.xpath("//a[@class='cardcomponent__Title-sc-11bhbdb-3 eCJUYb']/@href")
        for href in hrefs:
            page = requests.get('https://old.prozorro.sale' + href, headers=headers)
            tree = html.fromstring(page.content)
            hashIDs = tree.xpath('//*[@id="__next"]/main/header/div/div/p[2]/text()')
            for hashID in hashIDs:
                page = requests.get('https://procedure.prozorro.sale/api/registry/objects/' + hashID[27:],
                                    headers=headers)
                data_json = page.json()
                try:
                    email = data_json['relatedOrganizations']['currentTenant']['contactPoint']['email']
                    phone = data_json['relatedOrganizations']['currentTenant']['contactPoint']['telephone']
                except KeyError:
                    email = 'orenda.tsbgalcontract@gmail.com'
                    phone = 'None'
                registryObjectId = data_json['registryObjectId']
                registryObjectItems = data_json['registryObjectItems'][0]
                LotName = registryObjectItems['basicInfo']['description']['uk_UA']
                registryObjectId = data_json['registryObjectId']
                datePublished = data_json['datePublished']
                GCLink = 'https://sales.tsbgalcontract.org.ua/asset_rent/' + registryObjectId
                dateNow = datetime.now()
                if len(str(dateNow.month)) == 1:
                    month = "0" + str(dateNow.month)
                else:
                    month = str(dateNow.month)
                if len(str(dateNow.day)) == 1:
                    day = "0" + str(dateNow.day)
                else:
                    day = str(dateNow.day)
                year = str(dateNow.year)
                date = year + "-" + month + "-" + day
                #################################################
                myclient = pymongo.MongoClient(
                    "mongodb+srv://tsbgalcontract:mymongodb26@cluster0.kppkt.mongodb.net/test")
                mydb = myclient["Rent"]
                mycol = mydb["RentRegisterEmail"]
                document = {'registryObjectId': registryObjectId}
                present = mycol.find_one(document)
                if (str(present) == "None") and (date == str(datePublished)[0:10]):
                    mycol.insert_one(document)
                    tgIDs = ['705713759', '155840708', '840039085', '5475658482', '979180357']
                    for tgID in tgIDs:
                        try:
                            bot.send_message(tgID, f"Новий об'єкт оренди:\n{LotName}\n{GCLink}\n{phone}")
                            print(f'{href} SENT')
                        except Exception:
                            pass
                    ############################################
                    sender_email = "orenda.tsbgalcontract@gmail.com"
                    if email == "":
                        receiver_email = "orenda.tsbgalcontract@gmail.com"
                    else:
                        receiver_email = email
                    password = "eugeyrmaaajakxnj"

                    LotNameEmail = LotName
                    LotLinkEmail = GCLink
                    LotNumberEmail = registryObjectId

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

                Звертаємо Вашу увагу, що в ЕТС «Прозорро.Продажі» опубліковано об`єкт оренди <a href="{LotLinkEmail}"> {LotNameEmail} </a> <a href="{LotLinkEmail}"> ({LotNumberEmail}) </a>
                Ви є чинним орендарем даних приміщень.
                Вчасно подати заяву на продовження договору оренди та зареєструватись на участь в електронному аукціоні Ви зможете безкоштовно на електронному майданчику Товарно-сировинної біржі Галконтракт.

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
                    print('https://procedure.prozorro.sale/api/registry/objects/' + hashID[27:])
                    print('Надіслано')
                else:
                    print('https://procedure.prozorro.sale/api/registry/objects/' + hashID[27:])
                    print("Існуючий об'єкт, або не сьогоднішня дата")

    while True:
        try:
            ObjectsOfRent()
            time.sleep(60)
        except:
            bot.send_message(155840708, str(traceback.format_exc()))
            print(traceback.format_exc())
