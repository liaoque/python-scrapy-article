import requests
import cls
import weibo
import xueqiu


def commitMsg(msg):
    return msg


def gpt(msg):
    url = "https://quote.eastmoney.com/newapi/jgdc"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }

    msg = commitMsg(msg)
    response = requests.post(url, {"msg": msg}, headers=headers)
    codes2 = response.json()
    return codes2


def run(cursor):
    data = cls.queryData(cursor)
    for item in data:
        commit = gpt(item['text'])
        cls.saveCommit(cursor, item['id'], commit)

    data = weibo.queryData(cursor)
    for item in data:
        commit = gpt(item['text'])
        weibo.saveCommit(cursor, item['id'], commit)

    data = xueqiu.queryData(cursor)
    for item in data:
        commit = gpt(item['text'])
        xueqiu.saveCommit(cursor, item['id'], commit)

    pass
