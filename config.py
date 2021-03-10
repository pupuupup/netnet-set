def url_profile(s):
    return 'https://www.set.or.th/set/companyprofile.do?symbol='+s+'&language=en&country=US'

def url_highlights(s):
    return 'https://www.set.or.th/set/companyhighlight.do?symbol='+s+'&language=en&country=US'

def url_finance(s):
    return 'https://www.set.or.th/set/companyfinance.do?symbol='+s+'&language=en&country=US&type=balance'

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2',
    'Accept' : 'text/html, image/jpeg, image/png, text/*, image/*, */*',
    'Accept-Language': 'en-us',
    'Accept-Charset' : 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'Keep-Alive': '300',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0'
}

url = {
    'profile': url_profile,
    'highlights': url_highlights,
    'finance': url_finance
}

data = 'stock.csv'
