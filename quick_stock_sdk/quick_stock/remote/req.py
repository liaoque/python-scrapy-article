import requests
import numpy as np
from datetime import datetime

_headers = {
    "HOST": "push2his.eastmoney.com",
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}
def getDF(url, cookie=None, headers=None):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["data"]["klines"]
    else:
        raise Exception("无法获取股票信息")

def postDF(url, data, cookie=None, headers=None):
    pass
