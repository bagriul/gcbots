import time
import traceback
import requests
from lxml import html
import pymongo
import telebot
from threading import Thread

bot = telebot.TeleBot('5825750976:AAHf2LaO7jj4x540bIgGQaukxu_Ttxdh60w')


def run():
    def Bot():
        while True:
            try:
                @bot.message_handler(commands=['start'])
                def start_message(message):
                    myclient = pymongo.MongoClient(
                        "mongodb+srv://tsbgalcontract:mymongodb26@cluster0.kppkt.mongodb.net/test")
                    mydb = myclient["Rent"]
                    mycol = mydb["3iBot"]
                    document = {'type': 'user', 'userId': message.from_user.id}
                    present = mycol.find_one(document)
                    if str(present) == "None":
                        mycol.insert_one(document)
                    else:
                        pass

                bot.polling(none_stop=True)
            except:
                bot.send_message(155840708, str(traceback.format_exc()))
                print(traceback.format_exc())

    def Main():
        while True:
            try:
                def WriteToMongo():
                    myclient = pymongo.MongoClient(
                        "mongodb+srv://tsbgalcontract:mymongodb26@cluster0.kppkt.mongodb.net/test")
                    mydb = myclient["Rent"]
                    mycol = mydb["3iBot"]
                    document = {'auctionID': auctionID}
                    present = mycol.find_one(document)
                    if str(present) == "None":
                        mycol.insert_one(document)
                        users = mycol.find({'type': {'$exists': True}})
                        for user in users:
                            bot.send_message(str(user['userId']),
                                             f'Новий аукціон\nПосилання: https://prozorro.sale/auction/{auctionID}')
                    else:
                        pass

                def ObjectOfRent():
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
                        "Accept-Encoding": "*",
                        "Connection": "keep-alive"
                    }
                    pages = [
                        "https://old.prozorro.sale/auction/search?status=active.rectification&stream=legitimatePropertyLease&auctionType=priorityEnglish&offset=20"]
                    for page in pages:
                        webPage = requests.get(page, headers=headers)
                        tree = html.fromstring(webPage.content)
                        hrefs = tree.xpath("//a[@class='cardcomponent__Title-sc-11bhbdb-3 eCJUYb']/@href")
                        for href in hrefs:
                            webPage = requests.get("https://old.prozorro.sale/" + href, headers=headers)
                            print("https://old.prozorro.sale/" + href)
                            tree = html.fromstring(webPage.content)
                            hash = tree.xpath('//*[@id="__next"]/main/header/div/div/div/p/text()')
                            hashID = str(hash)[29:-2]

                            webPage = requests.get('https://procedure.prozorro.sale/api/procedures/' + hashID,
                                                   headers=headers)
                            procedure_json = webPage.json()
                            global auctionID
                            auctionID = str(procedure_json['auctionId'])
                            global tenant
                            tenant_list = procedure_json['relatedOrganizations']['currentTenants']
                            for tenant in tenant_list:
                                tenant = tenant['identifier']['id']

                            tenants = ['40000891', '38994526', '19324053', '37357084', '22600114', '30165865',
                                       '30994225',
                                       '40750641']
                            if tenant in tenants:
                                WriteToMongo()
                    time.sleep(120)

                ObjectOfRent()
            except:
                bot.send_message(155840708, str(traceback.format_exc()))
                print(traceback.format_exc())

    if __name__ == "__main__":
        t1 = Thread(target=Bot)
        t2 = Thread(target=Main)
        t1.start()
        t2.start()
