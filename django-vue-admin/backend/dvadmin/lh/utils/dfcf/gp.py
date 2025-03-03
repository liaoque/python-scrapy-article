
import requests

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
}

def GetGjList (code) :
    prefix = '0.'
    code3 = code[0:3]
    if code3 == '688':
        prefix = '1.'
    elif (code3 ==  '000') :
        prefix = '0.'
    elif (code3 ==  '002') :
        prefix = '0.'
    elif (code3 ==  '300') :
        prefix = '0.'
    elif (code3[0:2] == '60'):
        prefix = '1.'

    url = """https://push2his.eastmoney.com/api/qt/stock/kline/get"""
    params= {
        "code": code,
        "cb": '',
        "secid": prefix + code,
        "ut": '',
        "fields1": 'f1,f2,f3,f4,f5,f6',
        "fields2": 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
        "klt": 101,
        "fqt": 1,
        "end": '20500101',
        "lmt": '250',
    }
    response = requests.get(url, params=params, headers=headers)
    return response.json()



