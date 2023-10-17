import time
import traceback
import requests
from lxml import html
import pymongo
import telebot
from requests.exceptions import ConnectionError

bot = telebot.TeleBot('5917740192:AAHWm1YUkxO5cLpcUyP8v3I5enxtTC993vA')


def run():
    while True:
        try:
            def WriteToMongo():
                myclient = pymongo.MongoClient(
                    "mongodb+srv://tsbgalcontract:mymongodb26@cluster0.kppkt.mongodb.net/test")
                mydb = myclient["Rent"]
                mycol = mydb["ObjectsNoTenant"]
                document = {'auctionID': auctionID}
                present = mycol.find_one(document)
                if str(present) == "None":
                    mycol.insert_one(document)
                    users = ['155840708', '840039085', '5475658482', '705713759', '979180357', '766345430']
                    for user in users:
                        bot.send_message(user, f'Посилання: https://prozorro.sale/auction/{auctionID}')
                else:
                    pass

            def ObjectOfRent():
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
                    "Accept-Encoding": "*",
                    "Connection": "keep-alive"
                }
                pages = [
                    "https://old.prozorro.sale/?stream=legitimatePropertyLease&auctionType=english&item_region=79%E2%80%9382&item_region=43%E2%80%9345&item_region=88%E2%80%9390&item_region=76%E2%80%9378&item_region=46%E2%80%9348&item_region=29%E2%80%9332&item_region=21%E2%80%9324&item_region=07%E2%80%9309&item_region=01%E2%80%9306&item_region=18%E2%80%9320&item_region=58%E2%80%9360&item_region=14%E2%80%9317&offset=20&edrpou=42964094&edrpou=42767945&edrpou=43023403&edrpou=42891875&edrpou=43173325&edrpou=42899921&edrpou=43015722&edrpou=42769539&edrpou=42956062&edrpou=44223324&edrpou=21295778&edrpou=19030825&edrpou=00032945&status=active.tendering&status=active.rectification"]
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

                        WriteToMongo()
                time.sleep(60)

            ObjectOfRent()
        except ConnectionError:
            pass
        except:
            bot.send_message(155840708, str(traceback.format_exc()))
            print(traceback.format_exc())
