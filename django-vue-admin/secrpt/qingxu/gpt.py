import requests
from qingxu.cls import cls
import weibo
import xueqiu
import re
import jieba
import nltk
import time
from nltk.corpus import stopwords
import sqlite3

nltk.download('stopwords')
stop_words = set(stopwords.words('chinese'))  # 需要下载中文停用词表


def clean_text(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)  # 去除多余空格
    text = re.sub(r'[^\w\s]', '', text)  # 去除标点符号
    # 进一步清洗可以根据需要添加
    return text


def tokenize(text):
    return ' '.join(jieba.cut(text))


def commitMsg(msg):

    msg = clean_text(msg)
    msg = tokenize(msg)
    msg = """
    请分析以下文本的情感，判断是积极的或者是消极的或者是中性的，积极返回1，消极返回-1,中性返回0，不要返回（-1,0,1）之外任何数据
    """ + msg
    return msg


def gpt(msg):
    time.sleep(3)
    url = "http://ss.qq2021.com/v1/tmp/message"
    headers = {
        'Content-Type': 'application/json',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }

    msg = commitMsg(msg)
    response = requests.post(url, json={"prompt": msg, 'user_id':"0"}, headers=headers)
    codes2 = response.json()
    return codes2


def run(cursor, conn):
    data = cls.queryData(cursor)
    for item in data:
        codes2 = gpt(item['content'])
        if "data" in codes2 and "content" in codes2["data"]:
            content2 = content = codes2["data"]["content"]
            if "积极" in content2:
                content = "1"
            elif "中性" in content2:
                content = "0"
            elif "消极" in content2:
                content = "-1"
            elif content2 not in [0, 1, -1, "0", "1", "-1"]:
                content = "0"
            cls.saveCommit(cursor, item['tid'], content)
            conn.commit()

    data = weibo.queryData(cursor)
    for item in data:
        codes2 = gpt(item['content'])
        if "data" in codes2 and "content" in codes2["data"]:
            content2 = content = codes2["data"]["content"]
            if "积极" in content2:
                content = "1"
            elif "中性" in content2:
                content = "0"
            elif "消极" in content2:
                content = "-1"
            elif content2 not in [0, 1, -1, "0", "1", "-1"]:
                content = "0"
            weibo.saveCommit(cursor, item['tid'], content)
            conn.commit()

    data = xueqiu.queryData(cursor)
    for item in data:
        codes2 = gpt(item['content'])
        if "data" in codes2 and "content" in codes2["data"]:
            content2 = content = codes2["data"]["content"]
            if "积极" in content2:
                content = "1"
            elif "中性" in content2:
                content = "0"
            elif "消极" in content2:
                content = "-1"
            elif content2  not in [0,1,-1, "0", "1", "-1"]:
                content = "0"
            xueqiu.saveCommit(cursor, item['tid'], content)
            conn.commit()

    pass


def compute():

    conn = sqlite3.connect('v1/qingxu.db', isolation_level=None)
    conn.row_factory = sqlite3.Row
    # 创建一个Cursor:
    cursor = conn.cursor()

    gpt.run(cursor, conn)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    compute()
