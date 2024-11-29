import requests
from datetime import datetime

# https://www.cls.cn/v3/depth/home/assembled/1000?app=CailianpressWeb&os=web&sv=8.4.6&sign=9f8797a1f4de66c2370f7a03990d2737


# https://www.cls.cn/detail/1871761

# https://www.cls.cn/v3/depth/home/assembled/1003?app=CailianpressWeb&os=web&sv=8.4.6&sign=9f8797a1f4de66c2370f7a03990d2737
"""
 {app: "CailianpressWeb",os: "web",sv: "8.4.6"}
 p(a({}, r))
  function a(e) {
            for (var t = 1; t < arguments.length; t++) {
                var n = null != arguments[t] ? arguments[t] : {};
                t % 2 ? i(Object(n), !0).forEach((function(t) {
                    r(e, t, n[t])
                }
                )) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : i(Object(n)).forEach((function(t) {
                    Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t))
                }
                ))
            }
            return e
        }
 e.exports = function(e) {
            var t = e && s(u(e).map((function(t) {
                return c(t, e[t])
            }
            )));
            return t = r.sync(t),
            t = o(t)
        }

"""


# 财联社头条
def clstop(page):
    url = "https://www.cls.cn/v3/depth/home/assembled/1000?app=CailianpressWeb&os=web&sv=8.4.6&sign=9f8797a1f4de66c2370f7a03990d2737&page=" + str(
        page)
    headers = {
        "cookie": "SUB=_2A25KQYrPDeRhGeVL7FsT8irMyD2IHXVpPoIHrDV8PUNbmtAGLWjSkW9NTD9Yt3m0jJK7Ip88YDDdqn-eC8TAC_r1;",
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    data = response.json()["data"]
    data2 = []
    for item in data["top_article"]:
        for item2 in item["article_rec"]:
            data2.append({
                "id": item2["article_id"],
                "text": item2["brief"],
                "created_at": item2["ctime"],
                "type": 1,
            })
    for item in data["depth_list"]:
        data2.append({
            "id": item["article_id"],
            "text": item["brief"],
            "created_at": item["ctime"],
            "type": 1,
        })

    if len(data2) == 0:
        return []

    return data


def clsaa(page):
    url = "https://www.cls.cn/v3/depth/home/assembled/1003?app=CailianpressWeb&os=web&sv=8.4.6&sign=9f8797a1f4de66c2370f7a03990d2737&page=" + str(
        page)
    headers = {
        "cookie": "SUB=_2A25KQYrPDeRhGeVL7FsT8irMyD2IHXVpPoIHrDV8PUNbmtAGLWjSkW9NTD9Yt3m0jJK7Ip88YDDdqn-eC8TAC_r1;",
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    data = response.json()["data"]
    data2 = []
    for item in data["top_article"]:
        for item2 in item["article_rec"]:
            data2.append({
                "id": item2["article_id"],
                "text": item2["brief"],
                "created_at": item2["ctime"],
                "type": 2,
            })
    for item2 in data["depth_list"]:
        data2.append({
            "id": item2["article_id"],
            "text": item2["brief"],
            "created_at": item2["ctime"],
            "type": 2,
        })

    if len(data2) == 0:
        return []
    return data


def run(cursor):
    data = []

    # 查最大的id
    minIdTop = queryMaxId(cursor, 1)
    minIdaa = queryMaxId(cursor, 2)
    ids = []

    for i in range(100):

        # 爬头条, 找到id相同的位置
        data2 = clstop(i)
        for item in data2:
            if item['id'] in ids:
                continue
            if item["id"] == minIdTop:
                break
            data.append(item)
            ids.append(item['id'])

        # 爬A, 找到id相同的位置
        data2 = clsaa(i)
        for item in data2:
            if item['id'] in ids:
                continue
            if item["id"] == minIdaa:
                break
            data.append(item)
            ids.append(item['id'])

    if len(data) > 0:
        saveData(cursor, data)


def queryMaxId(cursor, type):
    cursor.execute('SELECT tid FROM m_cls WHERE type=? order by id desc', (type,))
    values = cursor.fetchall()
    if len(values) == 0:
        return 0
    return values[0]['tid']


def saveData(cursor, data):
    for item in data:
        cursor.execute('INSERT INTO m_cls (tid, content, created_at, type) VALUES (?, ?, ?, ?)',
                       (item['id'], item['text'], item['created_at'], item['type'],))


def queryData(cursor):
    cursor.execute('SELECT tid FROM m_cls WHERE commit is null order by id desc')
    values = cursor.fetchall()
    return values


def saveCommit(cursor, id, commit):
    cursor.execute('update m_cls set commit = ? where id = ?', (commit, id,))


def queryCommitPoint(cursor, created_at):
    cursor.execute('SELECT count(commit) c FROM m_cls where created_at = ? order by id desc', (created_at))
    values = cursor.fetchall()
    if len(values) == 0:
        return 0
    total = values[0]['c']

    cursor.execute('SELECT count(commit) c FROM m_cls  where commit =1 and created_at = ? order by id desc',
                   (created_at))
    values = cursor.fetchall()
    if len(values) == 0:
        up = 0
    else:
        up = values[0]['c']

    cursor.execute('SELECT count(commit) c FROM m_cls  where commit =0 and created_at = ? order by id desc',
                   (created_at))
    values = cursor.fetchall()
    if len(values) == 0:
        down = 0
    else:
        down = values[0]['c']
    return (up - down) / total


if __name__ == "__main__":
    pass
