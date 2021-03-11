# -*- coding: utf-8 -*-

import csv
import config
import grequests
import re
from lxml import html
from tqdm import tqdm
import codecs
import time


def importData():
    with open(config.data, 'rb') as f:
        reader = csv.reader(codecs.iterdecode(f, encoding="ISO-8859-1"))
        return list(reader)

def getSymbol(data):
    print("Getting Symbol ...")
    symbolsWithHeader = list(map(lambda x: x[0], data))
    symbols = symbolsWithHeader[ 2: len(symbolsWithHeader) ]
    return list(map(lambda x: {'symbol': x}, symbols))

def toNakedShareNumber(word):
    return float(re.sub("\D", "", word))

def toNakedPriceNumber(word):
    word = word.replace(',', '')
    return float(word)

def toNakedFinanceNumber(word):
    return float(word.replace(',',''))

def getProfileUrl(data):
    return config.url['profile'](data['symbol'])

def getPriceUrl(data):
    return config.url['highlights'](data['symbol'])

def getFinanceUrl(data):
    return config.url['finance'](data['symbol'])

def scrapeAndFormatShare(page):
    if(page == None): return '-1'
    tree = html.fromstring(page.content)
    share = tree.xpath('//div[text()="Listed Share"]/following-sibling::div/text()')
    share = '0' if not share else share[0]
    return toNakedShareNumber(share)

def getShare(datas):
    print("Getting Share ...")
    urls = list(map(getProfileUrl, datas))
    rs = (grequests.get(u) for u in urls)
    pages = tqdm(grequests.imap(rs))
    shares = list(map(scrapeAndFormatShare, pages))
    for i in range(len(datas)):
        datas[i].update({'share': shares[i]})
    return datas

def scrapeAndFormatPrice(page):
    if(page == None): return '-1'
    tree = html.fromstring(page.content)
    prices = tree.xpath('//td[text()="Last Price(Baht)"]/following-sibling::td/text()')
    try:
        price = prices[len(prices) - 1]
    except:
        price = '0'
    return toNakedPriceNumber(price)

def getPrice(datas):
    print("Getting Price ...")
    urls = list(map(getPriceUrl, datas))
    rs = (grequests.get(u) for u in urls)
    pages = tqdm(grequests.imap(rs))
    prices = list(map(scrapeAndFormatPrice, pages))
    for i in range(len(datas)):
        datas[i].update({'price': prices[i]})
    return datas

def scrapeAndFormatFinance(page):
    if(page == None): return {}
    t = html.fromstring(page.content).xpath
    finance = {
        "cash": t('//td[text()="CASH AND CASH EQUIVALENTS"]/following-sibling::td/text()'),
        "investment": t('//td[text()="SHORT-TERM INVESTMENTS"]/following-sibling::td/text()'),
        "recievable": t('//td[text()="TRADE ACCOUNTS AND OTHER RECEIVABLE"]/following-sibling::td/text()'),
        "asset": t('//td[text()="TOTAL CURRENT ASSETS"]/following-sibling::td/text()'),
        "inventory": t('//td[text()="INVENTORIES"]/following-sibling::td/text()'),
        "liability": t('//td[text()="TOTAL LIABILITIES"]/following-sibling::td/text()')
    }
    finance = dict(zip(finance, map(lambda x: 0 if not x else x[0], finance.values())))
    finance = dict(zip(finance, map(lambda x: 0 if x==0  else toNakedFinanceNumber(x), finance.values())))
    finance = dict(zip(finance, map(lambda x: x*1000000, finance.values())))
    return finance

def getFinance(datas):
    print("Getting Finance ...")
    urls = map(getFinanceUrl, datas)
    rs = (grequests.get(u) for u in urls)
    pages = tqdm(grequests.imap(rs))
    finances = list(map(scrapeAndFormatFinance, pages))
    for i in range(len(datas)):
        datas[i].update(finances[i])
    return datas

def calculateNCAV(data):
    try:
        return (data['asset'] - data['liability'])/data['share']
    except:
        return 'N/A'

def getNCAV(datas):
    print("Getting NCAV ...")
    ncav = list(map(calculateNCAV, datas))
    for i in range(len(datas)):
        datas[i].update({'ncav': ncav[i]})
    return datas

def calculateNNWC(data):
    try:
        return ((data['cash'] + data['investment']) +\
               (0.75 * data['recievable']) +\
               (0.5 * data['inventory']) -\
               (data['liability']))/data['share']
    except:
        return 'N/A'

def getNNWC(datas):
    print("Getting NNWC ...")
    nnwc = list(map(calculateNNWC, datas))
    for i in range(len(datas)):
        datas[i].update({'nnwc': nnwc[i]})
    return datas

def calculatePercent(data):
    try:
        nnwc = str(round((data['price']/data['nnwc'])*100, 2))
    except:
        nnwc = -1
    try:
        ncav = str(round((data['price']/data['ncav'])*100, 2))
    except:
        ncav = -1
    if data['nnwc'] == 'N/A':
        data['nnwc'] = -1
    if data['ncav'] == 'N/A':
        data['ncav'] = -1
    return {
        'symbol': data['symbol'],
        'nnwc_percent': 'N/A' if int(data['nnwc']) < 0 else nnwc,
        'ncav_percent': 'N/A' if int(data['ncav']) < 0 else ncav
    }

def displayEach(data):
    print("=================")
    print(data['symbol'])
    if(data['nnwc_percent'] == 'N/A'):
        pass
    elif(data['nnwc_percent'] >= 0 and data['nnwc_percent'] < 70):
        color_print("nnwc " + data['nnwc_percent'] + "%", color='green')
    elif(data['nnwc_percent'] >= 70 and data['nnwc_percent'] < 100):
        color_print("nnwc " + data['nnwc_percent'] + "%", color='yellow')
    elif(data['nnwc_percent'] >= 100):
        color_print("nnwc " + data['nnwc_percent'] + "%", color='red')
    if(data['ncav_percent'] == 'N/A'):
        pass
    elif(data['ncav_percent'] >= 0 and data['ncav_percent'] < 70):
        color_print("ncav " + data['ncav_percent'] + "%", color='green')
    elif(data['ncav_percent'] >= 70 and data['ncav_percent'] < 100):
        color_print("ncav " + data['ncav_percent'] + "%", color='yellow')
    elif(data['ncav_percent'] >= 100):
        color_print("ncav " + data['ncav_percent'] + "%", color='red')

def getPercent(datas):
    percents = list(map(calculatePercent, datas))
    for i in range(len(datas)):
        datas[i].update(percents [i])
    return datas

def display(datas):
    map(displayEach, datas)

def main():
    datas = importData()
    datas = getSymbol(datas)
    datas = getShare(datas)
    datas = getPrice(datas)
    datas = getFinance(datas)
    datas = getNCAV(datas)
    datas = getNNWC(datas)
    datas = getPercent(datas)
    print(datas)
    toCSV(datas)

def toCSV(datas):
    keys = datas[0].keys()
    with open('final.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(datas)

main()

