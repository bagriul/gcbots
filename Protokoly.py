import json
import schedule
import requests
import time
from lxml import html
import httplib2
import os
from datetime import datetime
from datetime import timedelta
import telebot
import threading
from dateutil.relativedelta import relativedelta
from dateutil.rrule import *
import browser_cookie3
import traceback
import gspread
import re
from selenium.webdriver import FirefoxOptions
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver
from gspread.exceptions import APIError
from bs4 import BeautifulSoup as bs
from webdriver_manager.chrome import ChromeDriverManager

bot = telebot.TeleBot('5526110130:AAFPKfy-mHPqcqXgHi_d3rui_1Qq_OEDPc4')


def run():
    def UpdateTable():
        gc = gspread.service_account('client_secret.json')
        sh = gc.open_by_key('1hQeYBLB8QVmiHwOJIrmy6IIJCoMwvtC_JYLbQJOFiAI')
        global ws
        ws = sh.get_worksheet(0)
        ws.update_title('Оновлення...')
        time.sleep(1)
        check_row = ws.col_values(9)[1:]
        for check in check_row:
            cell = ws.find(check)
            time.sleep(2)
            status = ws.cell(cell.row, 7).value
            time.sleep(1)
            protokol = ws.cell(cell.row, 6).value
            time.sleep(1)
            checkForLink = ws.cell(cell.row, 2).value
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.google.com/'
            }
            request = requests.get(f"https://marketplace.prozorro.sale/auction/{checkForLink}", headers=headers)
            soup = bs(request.content, 'html.parser')
            newstatus = soup.find('div', class_='news-card__status').text.strip()
            newprotokol_div = soup.find('div', class_='table-info__date-opening')
            try:
                newprotokol = newprotokol_div.find_all('span')[1].text[:-6]
            except AttributeError:
                newprotokol = "Немає"
            if status != newstatus:
                ws.update_cell(cell.row, 7, newstatus)
                time.sleep(1)
            if protokol != newprotokol:
                ws.update_cell(cell.row, 6, newprotokol)
                time.sleep(1)
            print(f'{checkForLink} Checked')
            time.sleep(1)

    def WriteToTable(auction_date, lotnumber, member):
        gc = gspread.service_account('client_secret.json')
        sh = gc.open_by_key('1hQeYBLB8QVmiHwOJIrmy6IIJCoMwvtC_JYLbQJOFiAI')
        ws = sh.get_worksheet(0)
        ws2 = sh.get_worksheet(1)
        check_row = ws.col_values(9)[1:]
        check_row2 = ws2.col_values(7)[1:]
        time.sleep(1)
        request = requests.get(f'https://marketplace.prozorro.sale/auction/{lotnumber}')
        soup = bs(request.content, 'html.parser')
        newstatus = soup.find('div', class_='news-card__status').text.strip()
        newprotokol_div = soup.find('div', class_='table-info__date-opening')
        try:
            newprotokol = newprotokol_div.find_all('span')[1].text[:-6]
        except AttributeError:
            newprotokol = "Немає"
        if (f'{member}{lotnumber}' in check_row) or (f'{member}{lotnumber}' in check_row2):
            pass
        else:
            linkP = f'https://prozorro.sale/auction/{lotnumber}'
            linkG = f'https://sales.tsbgalcontract.org.ua/auction/{lotnumber}'
            checker = f'{member}{lotnumber}'
            ws.append_row([auction_date, lotnumber, member, linkP, linkG, newprotokol, newstatus, '', checker])
            time.sleep(1)
            print(f'New {lotnumber}')
        time.sleep(1)

    def bids2():
        UpdateTable()
        time.sleep(60)
        startDate = datetime.now().date() - relativedelta(days=1)

        def BidsInfo(startDate):
            opts = selenium.webdriver.ChromeOptions()
            opts.add_argument('--headless')
            chrome_binary_path = r'C:\Users\Manager_2\Downloads\chrome-win64\chrome-win64\chrometest.exe'
            #opts.binary_location = chrome_binary_path
            driver = selenium.webdriver.Chrome(ChromeDriverManager().install(), options=opts)
            driver.get("https://sales.tsbgalcontract.org.ua/Login.aspx")
            username_field = driver.find_element("id", "eLogin")
            password_field = driver.find_element("id", "ePassword")
            login_button = driver.find_element("id", "btnLogin")
            username_field.send_keys("7timoor@gmail.com")
            password_field.send_keys("l689^544333")
            login_button.click()
            time.sleep(1)
            driver.get(
                f'https://sales.tsbgalcontract.org.ua/EditDataHandler.ashx?CN=0&CommandName=GetBids&page=1&rows=1000&sidx=b.dateModified&sord=desc&fvBidState_0=active&fvauctiondate_0=%20%3E%3D%20%27{startDate}%27&TimeMark=37624327')
            wait = WebDriverWait(driver, 30)
            wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/pre")))
            bidsText = driver.find_element("xpath", '/html/body/pre')
            bidsInfo = json.loads(bidsText.text)
            return bidsInfo

        data_json = BidsInfo(startDate)
        bids = data_json['rows']
        for bid in bids:
            auction_date = bid['auction_date'][0:10]
            auction_date_list = auction_date.split('-')
            auction_date = f'{auction_date_list[2]}.{auction_date_list[1]}.{auction_date_list[0]}'
            tenderID = bid['tenderID']
            short_name = bid['short_name']
            WriteToTable(auction_date, tenderID, short_name)
        ws.update_title('Протоколи')
        print('READY')
        print(datetime.now().time())
        time.sleep(1800)

    while True:
        try:
            bids2()
        except:
            bot.send_message(155840708, str(traceback.format_exc()))
            print(traceback.format_exc())
            time.sleep(120)
