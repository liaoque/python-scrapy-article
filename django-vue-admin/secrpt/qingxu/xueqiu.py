import requests


# https://xueqiu.com/query/v1/symbol/search/status.json?count=10&comment=0&symbol=SH000001&hl=0&source=all&sort=&page=1&q=&type=12&md5__1038=n4%2BxcDyDBDRD9jbD%2FD0YoY0QQeqmTvIhypD
# https://xueqiu.com/query/v1/symbol/search/status.json?count=10&comment=0&symbol=SH000001&hl=0&source=all&sort=&page=2&q=&type=12&md5__1038=n4jxR7exBCe05DI5YK0%3DGOQFqYvc4D%3DFWWa4D

def xueqiu(page):
    url = "https://xueqiu.com/query/v1/symbol/search/status.json?count=10&symbol=SH000001&md5__1038=eqRxcQqQqiwO3DsD7%2Bq0%3D3GQgg7f%3DD7TcGD&page=" + str(
        page)
    headers = {
        "cookie": "u=4493850983;",
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    cards = response.json()["list"]
    data = []
    for item in cards:
        data.append({
            "id": item["id"],
            "text": item["text"],
            "created_at": item["created_at"],
            "type": 1
        })
    return data


def run(cursor):
    data = []

    # 查最大的id
    weiboIdTop = queryMaxId(cursor)
    ids = []

    for i in range(100):

        # 爬微博, 找到id相同的位置
        data2 = xueqiu(i)
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
    cursor.execute('SELECT tid FROM m_xueqiu  order by id desc limit 1' )
    values = cursor.fetchall()
    if len(values) == 0:
        return 0
    return values[0]['tid']


def saveData(cursor, data):
    for item in data:
        cursor.execute('INSERT INTO m_xueqiu (tid, content, created_at, type) VALUES (?, ?, ?, ?)',
                       (item['id'], item['text'], item['created_at'], item['type'],))


def queryData(cursor):
    cursor.execute('SELECT tid FROM m_xueqiu WHERE commit is null order by id desc')
    values = cursor.fetchall()
    return values


def saveCommit(cursor, id, commit):
    cursor.execute('update m_xueqiu set commit = ? where id = ?', (commit, id,))


def queryCommitPoint(cursor, created_at):
    cursor.execute('SELECT count(commit) c FROM m_xueqiu where created_at = ? order by id desc limit 1', (created_at))
    values = cursor.fetchall()
    if len(values) == 0:
        return 0
    total = values[0]['c']

    cursor.execute('SELECT count(commit) c FROM m_xueqiu  where commit =1 and created_at = ? order by id desc limit 1', (created_at))
    values = cursor.fetchall()
    if len(values) == 0:
        up = 0
    else:
        up = values[0]['c']

    cursor.execute('SELECT count(commit) c FROM m_xueqiu  where commit =0 and created_at = ? order by id desc limit 1', (created_at))
    values = cursor.fetchall()
    if len(values) == 0:
        down = 0
    else:
        down = values[0]['c']
    return (up - down) / total