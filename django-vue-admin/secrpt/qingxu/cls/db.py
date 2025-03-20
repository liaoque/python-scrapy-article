import hashlib
import time
import urllib.parse
import requests

"""
财联社电报
https://www.cls.cn/nodeapi/updateTelegraphList?app=CailianpressWeb&category=&hasFirstVipArticle=1&lastTime=1742023017&os=web&rn=20&subscribedColumnIds=&sv=8.4.6&sign=8a6e608e20ca45750b590aad8412f60b

"""


def sign(url):
    sha1_hash = hashlib.sha1(url.encode()).hexdigest()

    # 对SHA-1的结果进行MD5哈希
    md5_hash = hashlib.md5(sha1_hash.encode()).hexdigest()
    return md5_hash


def dbnew():
    ### 电报
    url = 'https://www.cls.cn/nodeapi/updateTelegraphList'
    time.time()
    params = {
        "app": "CailianpressWeb",
        "category": "",
        "hasFirstVipArticle": "1",
        "lastTime": int(time.time()),
        "os": "web",
        "rn": "20",
        "subscribedColumnIds": "",
        "sv": "8.4.6",
    }

    query_string = urllib.parse.urlencode(params)
    params['sign'] = sign(query_string)
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(full_url, headers=headers)
    res = response.json()
    if "errno" in res and res["errno"] != 0:
        return
    data = res["data"]['roll_data']

    return data


if __name__ == '__main__':
    dbnew()