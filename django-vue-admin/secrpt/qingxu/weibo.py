import requests
from datetime import datetime


def weibo(page):
    url = "https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D%E4%B8%8A%E8%AF%81%E6%8C%87%E6%95%B0%26t%3D&page_type=searchall&page=" + str(
        page)
    headers = {
        "cookie": "SUB=_2A25KQYrPDeRhGeVL7FsT8irMyD2IHXVpPoIHrDV8PUNbmtAGLWjSkW9NTD9Yt3m0jJK7Ip88YDDdqn-eC8TAC_r1;",
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    cards = response.json()["data"]["cards"]

    data = []
    time_format = '%a %b %d %H:%M:%S %z %Y'
    for item in cards:
        if item["card_type"] == 11:
            for item2 in item["card_group"]:
                if item2["card_type"] == 9:
                    data.append({
                        "id": item2["mblog"]["id"],
                        "text": item2["mblog"]["text"],
                        "created_at": datetime.strptime(item2["mblog"]["created_at"], time_format),
                        "type": 1
                    })
            continue
        elif item["card_type"] == 9:
            data.append({
                "id": item["mblog"]["id"],
                "text": item["mblog"]["text"],
                "created_at": datetime.strptime(item["mblog"]["created_at"], time_format),
                "type": 1
            })
    if len(data) == 0:
        return []

    return data


def run(cursor):
    data = []

    # 查最大的id
    weiboIdTop = queryMaxId(cursor)
    ids = []

    for i in range(100):

        # 爬微博, 找到id相同的位置
        data2 = weibo(i)
        for item in data2:
            if item['id'] in ids:
                continue
            if item["id"] == weiboIdTop:
                break
            data.append(item)
            ids.append(item['id'])

    if len(data) > 0:
        saveData(cursor, data)


def queryMaxId(cursor):
    cursor.execute('SELECT tid FROM m_weibo  order by id desc')
    values = cursor.fetchall()
    if len(values) == 0:
        return 0
    return values[0]['tid']


def saveData(cursor, data):
    for item in data:
        cursor.execute('INSERT INTO m_weibo (tid, content, created_at, type) VALUES (?, ?, ?, ?)',
                       (item['id'], item['text'], item['created_at'], item['type'],))

def queryData(cursor):
    cursor.execute('SELECT tid FROM m_weibo WHERE commit is null order by id desc')
    values = cursor.fetchall()
    return values


def saveCommit(cursor, id, commit):
    cursor.execute('update m_weibo set commit = ? where id = ?', (commit, id,))


if __name__ == "__main__":
    pass
