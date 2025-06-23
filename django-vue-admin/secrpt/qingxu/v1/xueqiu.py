import requests
from qingxu import config
from qingxu.xueqiu import symbol
from datetime import datetime
from common import dingding,clean

# https://xueqiu.com/query/v1/symbol/search/status.json?count=10&comment=0&symbol=SH000001&hl=0&source=all&sort=&page=1&q=&type=12&md5__1038=n4%2BxcDyDBDRD9jbD%2FD0YoY0QQeqmTvIhypD
# https://xueqiu.com/query/v1/symbol/search/status.json?count=10&comment=0&symbol=SH000001&hl=0&source=all&sort=&page=2&q=&type=12&md5__1038=n4jxR7exBCe05DI5YK0%3DGOQFqYvc4D%3DFWWa4D


def run(cursor):
    if config.checkDefault("xueqiu"):
        return
    data = []

    # 查最大的id
    weiboIdTop = queryMaxId(cursor)
    ids = []

    for i in range(10):

        # 爬微博, 找到id相同的位置
        data2 = symbol.symbolCode("SH000001",i)
        for item in data2:
            if item['id'] in ids:
                continue
            # if item["id"] == weiboIdTop:
            #     break
            data.append(item)
            ids.append(item['id'])

    if len(data) > 0:
        saveData(cursor, data)


def queryMaxId(cursor):
    cursor.execute('SELECT tid FROM m_xueqiu  order by id desc limit 1' )
    values = cursor.fetchall()
    if len(values) == 0:
        return 0
    return values[0]['tid']

def exits(cursor, id, type):
    cursor.execute(
        'SELECT tid FROM m_xueqiu WHERE tid = %s AND type = %s ORDER BY id DESC',
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
            'INSERT INTO m_xueqiu (tid, content, created_at, type) VALUES (%s, %s, %s, %s)',
            (item['id'], item['text'], item['created_at'], item['type'])
        )
        cursor.execute(
            'INSERT INTO m_qingxu_report (table_id, table_name, created_at, isrun) VALUES (%s, %s, %s, %s)',
            (cursor.lastrowid, "m_xueqiu", item['created_at'], 0)
        )

def queryData(cursor):
    cursor.execute('SELECT tid,content FROM m_xueqiu WHERE commited IS NULL ORDER BY id DESC')
    values = cursor.fetchall()
    return values


def saveCommit(cursor, id, commit):
    cursor.execute(
        'UPDATE m_xueqiu SET commited = %s WHERE id = %s',
        (commit, id)
    )


def queryCommitPoint(cursor, created_at):
    cursor.execute(
        'SELECT COUNT(commited) c FROM m_xueqiu WHERE created_at = %s ORDER BY id DESC LIMIT 1',
        (created_at,)
    )
    values = cursor.fetchall()
    if len(values) == 0:
        return 0
    total = values[0]['c']

    cursor.execute(
        'SELECT COUNT(commited) c FROM m_xueqiu WHERE commited = 1 AND created_at = %s ORDER BY id DESC LIMIT 1',
        (created_at,)
    )
    values = cursor.fetchall()
    if len(values) == 0:
        up = 0
    else:
        up = values[0]['c']

    cursor.execute(
        'SELECT COUNT(commited) c FROM m_xueqiu WHERE commited = 0 AND created_at = %s ORDER BY id DESC LIMIT 1',
        (created_at,)
    )
    values = cursor.fetchall()
    if len(values) == 0:
        down = 0
    else:
        down = values[0]['c']
    return (up - down) / total