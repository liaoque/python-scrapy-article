import requests
import cls
import weibo
import xueqiu
import re
import jieba


stop_words = set(stopwords.words('chinese'))  # 需要下载中文停用词表


def clean_text(text):
    text = re.sub(r'\s+', ' ', text)  # 去除多余空格
    text = re.sub(r'[^\w\s]', '', text)  # 去除标点符号
    # 进一步清洗可以根据需要添加
    return text


def tokenize(text):
    return ' '.join(jieba.cut(text))


def commitMsg(msg):

    msg = msg.apply(clean_text)
    msg = msg.apply(tokenize)

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
