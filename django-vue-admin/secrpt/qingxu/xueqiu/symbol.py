import os

import requests
from datetime import datetime, timezone
from urllib.parse import urlencode, quote_plus
import execjs

def symbolCode(symbol, page):
    # url = "https://xueqiu.com/query/v1/symbol/search/status.json?count=100&symbol=SH000001&md5__1038=eqRxcQqQqiwO3DsD7%2Bq0%3D3GQgg7f%3DD7TcGD&page=" + str(
    #     page)

    url =  "https://xueqiu.com/query/v1/symbol/search/status.json"
    params = {
        "count": "100",
        "symbol": symbol,
        "page": page,
    }
    headers = {
        "cookie": "u=4493850983;",
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }

    query_string = urlencode(params)
    url = f"{url}?{query_string}"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ctx = execjs.compile(open(current_dir + '/sign/sign.js').read())
    md51038 = ctx.call('signNew', quote_plus(url))
    url = f"{url}&md5__1038={md51038}"

    response = requests.get(url, headers=headers)
    cards = response.json()["list"]
    data = []
    for item in cards:
        created_at = datetime.utcfromtimestamp(int(item["created_at"]/1000)).strftime("%Y-%m-%d %H:%M:%S")

        data.append({
            "id": item["id"],
            "text": item["text"],
            "created_at": created_at,
            "type": 1
        })
    return data


if __name__ == '__main__':
    symbolCode("SH000001", 1)
