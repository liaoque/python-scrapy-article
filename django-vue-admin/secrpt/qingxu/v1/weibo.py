from turtle import up, down

import requests
from datetime import datetime
from qingxu import config
from common import dingding,clean

def weibo(page):
    url = "https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D%E4%B8%8A%E8%AF%81%E6%8C%87%E6%95%B0%26t%3D&page_type=searchall&page=" + str(
        page)
    headers = {
        "cookie": "SUB=_2A25KQYrPDeRhGeVL7FsT8irMyD2IHXVpPoIHrDV8PUNbmtAGLWjSkW9NTD9Yt3m0jJK7Ip88YDDdqn-eC8TAC_r1;",
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    res = response.json()
    if res["ok"] != 1:
        if "这里还没有内容" not in response.content.decode("utf-8"):
            dingding.dingding("weibo stop " + response.content.decode("utf-8"))
        return []
    cards = res["data"]["cards"]

    data = []
    time_format = '%a %b %d %H:%M:%S %z %Y'
    for item in cards:
        if item["card_type"] == 11:
            for item2 in item["card_group"]:
                if item2["card_type"] == 9:
                    data.append({
                        "id": item2["mblog"]["id"],
                        "text": item2["mblog"]["text"],
                        "created_at": datetime.strptime(item2["mblog"]["created_at"], time_format).strftime(
                            "%Y-%m-%d %H:%M:%S"),
                        "type": 1
                    })
            continue
        elif item["card_type"] == 9:
            data.append({
                "id": item["mblog"]["id"],
                "text": item["mblog"]["text"],
                "created_at": datetime.strptime(item["mblog"]["created_at"], time_format).strftime("%Y-%m-%d %H:%M:%S"),
                "type": 1
            })
    if len(data) == 0:
        return []

    return data


def run(cursor):
    if config.checkDefault("weibo"):
        return
    data = []

    # 查最大的id
    weiboIdTop = queryMaxId(cursor)
    ids = []
    b = False
    for i in range(10):

        if b:
            break

        # 爬微博, 找到id相同的位置
        data2 = weibo(i)
        for item in data2:
            if item['id'] in ids:
                continue
            # if item["id"] == weiboIdTop:
            #     b = True
            #     break
            data.append(item)
            ids.append(item['id'])

    if len(data) > 0:
        saveData(cursor, data)


def queryMaxId(cursor):
    cursor.execute('SELECT tid FROM m_weibo  order by id desc limit 1')
    values = cursor.fetchall()
    if len(values) == 0:
        return 0
    return values[0][0]


def exits(cursor, id, type):
    # cursor.execute('SELECT tid FROM m_weibo where tid = ? and type = ? order by id desc', (id, type,))
    cursor.execute(
        'SELECT tid FROM m_weibo WHERE tid = %s AND type = %s ORDER BY id DESC',
        (id, type)
    )
    values = cursor.fetchall()
    return len(values) > 0


def saveData(cursor, data):
    for item in data:
        if exits(cursor, item['id'], item['type']):
            continue
        item['text'] = clean.clean_text(item['text'])
        cursor.execute(
            'INSERT INTO m_weibo (tid, content, created_at, type) VALUES (%s, %s, %s, %s)',
            (item['id'], item['text'], item['created_at'], item['type'])
        )
        cursor.execute(
            'INSERT INTO m_qingxu_report (table_id, table_name, created_at, isrun) VALUES (%s, %s, %s, %s)',
            (cursor.lastrowid, "m_weibo", item['created_at'], 0)
        )


def queryData(cursor):
    cursor.execute('SELECT tid,content FROM m_weibo WHERE commited is null order by id desc')
    values = cursor.fetchall()
    return values


def saveCommit(cursor, id, commit):
    cursor.execute(
        'UPDATE m_weibo SET commited = %s WHERE id = %s',
        (commit, id)
    )


def queryCommitPoint(cursor, created_at):
    cursor.execute(
        'SELECT COUNT(commited) c FROM m_weibo WHERE created_at = %s ORDER BY id DESC LIMIT 1',
        (created_at,)
    )
    values = cursor.fetchall()
    if len(values) == 0:
        return 0
    # total = values[0]['c']
    total = values[0][0] if values else 0

    cursor.execute(
        'SELECT COUNT(commited) c FROM m_weibo WHERE commited = 1 AND created_at = %s ORDER BY id DESC LIMIT 1',
        (created_at,)
    )
    values = cursor.fetchall()
    up = values[0][0] if values else 0
    # if len(values) == 0:
    #     up = 0
    # else:
    #     up = values[0]['c']

    cursor.execute(
        'SELECT COUNT(commited) c FROM m_weibo WHERE commited = 0 AND created_at = %s ORDER BY id DESC LIMIT 1',
        (created_at,)
    )
    values = cursor.fetchall()
    down = values[0][0] if values else 0
    # if len(values) == 0:
    #     down = 0
    # else:
    #     down = values[0]['c']
    return (up - down) / total


if __name__ == "__main__":
    pass
