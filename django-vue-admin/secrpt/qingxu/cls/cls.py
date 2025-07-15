import requests
from common import dingding,clean
from qingxu import config
import hashlib
import datetime

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


def sign(url):
    sha1_hash = hashlib.sha1(url.encode()).hexdigest()

    # 对SHA-1的结果进行MD5哈希
    md5_hash = hashlib.md5(sha1_hash.encode()).hexdigest()
    return md5_hash


def parse(data):
    data2 = []

    for item in data["top_article"]:
        if len(item["article_rec"]) == 0:
            ctime = datetime.datetime.utcfromtimestamp(item["ctime"]).strftime("%Y-%m-%d %H:%M:%S")
            data2.append({
                "id": item["id"],
                "text": item["title"] + item["brief"],
                "created_at": ctime,
                "type": 2,
            })
            continue
        for item2 in item["article_rec"]:
            ctime = datetime.datetime.utcfromtimestamp(item2["ctime"]).strftime("%Y-%m-%d %H:%M:%S")
            data2.append({
                "id": item2["article_id"],
                "text": item2["name"] + item2["brief"],
                "created_at": ctime,
                "type": 1,
            })
    for item in data["depth_list"]:
        ctime = datetime.datetime.utcfromtimestamp(item["ctime"]).strftime("%Y-%m-%d %H:%M:%S")
        data2.append({
            "id": item["id"],
            "text": item["title"] + item["brief"],
            "created_at": ctime,
            "type": 1,
        })
    return data2

# 财联社头条
def clstop():
    path = "app=CailianpressWeb&os=web&sv=8.4.6"
    path = path + "&sign=" + sign(path)
    url = "https://www.cls.cn/v3/depth/home/assembled/1000?" + path
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    res = response.json()
    if "errno" in res and res["errno"] != 0:
        config.saveDefault("cls", "0")
        dingding.dingding("clstop " + response.text)
        return
    data = res["data"]
    data2 = parse(data)

    if len(data2) == 0:
        return []

    return data2


def clsaa():
    # a股
    path = "app=CailianpressWeb&os=web&sv=8.4.6"
    path = path + "&sign=" + sign(path)
    url = "https://www.cls.cn/v3/depth/home/assembled/1003?" + path
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    res = response.json()
    if "errno" in res and res["errno"] != 0:
        config.saveDefault("cls", "0")
        dingding.dingding("clstop " + response.text)
        return
    data = res["data"]
    data2 = parse(data)

    if len(data2) == 0:
        return []
    return data2


def run(cursor):
    if config.checkDefault("cls"):
        return
    data = []

    cleanAgain(cursor)
    # 查最大的id
    minIdTop = queryMaxId(cursor, 1)
    minIdaa = queryMaxId(cursor, 2)
    ids = []

    for i in range(1):

        # 爬头条, 找到id相同的位置
        data2 = clstop()
        for item in data2:
            if item['id'] in ids:
                continue
            if item["id"] == minIdTop:
                break
            data.append(item)
            ids.append(item['id'])

        # 爬A, 找到id相同的位置
        data2 = clsaa()
        for item in data2:
            if item['id'] in ids:
                continue
            if item["id"] == minIdaa:
                break
            data.append(item)
            ids.append(item['id'])

    if len(data) > 0:
        saveData(cursor, data)

def cleanAgain(cursor):
    cursor.execute('delete from m_cls where id in (select id from (SELECT id, content, count(1) as a FROM `m_cls` GROUP BY content) t where a > 1)')
    cursor.execute('delete from m_xueqiu where id in (select id from (SELECT id, content, count(1) as a FROM `m_xueqiu` GROUP BY content) t where a > 1)')
    cursor.execute('delete from m_weibo  where id in (select id from (SELECT id, content, count(1) as a FROM `m_weibo` GROUP BY content) t where a > 1)')



def queryMaxId(cursor, type):
    cursor.execute('SELECT tid FROM m_cls WHERE type=%s order by id desc limit 1', (type,))
    values = cursor.fetchall()
    if len(values) == 0:
        return 0
    return values[0][0]


def saveData(cursor, data):
    for item in data:
        if exits(cursor, item['id'], item['type']):
            continue
        item['text'] = clean.clean_text(item['text'])
        cursor.execute(
            'INSERT INTO m_cls (tid, content, created_at, type) VALUES (%s, %s, %s, %s)',
            (item['id'], item['text'], item['created_at'], item['type'])
        )
        cursor.execute(
            'INSERT INTO m_qingxu_report (table_id, table_name, created_at, isrun) VALUES (%s, %s, %s, %s)',
            (cursor.lastrowid, "m_cls", item['created_at'], 0)
        )


def exits(cursor, id, type):
    cursor.execute(
        'SELECT tid FROM m_cls where tid = %s and type = %s order by id desc',
        (id, type)
    )
    values = cursor.fetchall()
    return len(values) > 0


def queryData(cursor):
    cursor.execute('SELECT tid,content FROM m_cls WHERE commited is null order by id desc')
    values = cursor.fetchall()
    return values


def saveCommit(cursor, id, commited):
    cursor.execute('UPDATE m_cls set commited = %s where id = %s', (commited, id))


def queryCommitPoint(cursor, created_at):
    cursor.execute(
        'SELECT count(commited) c FROM m_cls where created_at = %s order by id desc limit 1',
        (created_at,)
    )
    values = cursor.fetchall()
    if len(values) == 0:
        return 0
    # total = values[0]['c']
    total = values[0][0] if values else 0

    cursor.execute(
        'SELECT count(commited) c FROM m_cls where commited =1 and created_at = %s order by id desc limit 1',
        (created_at,)
    )

    values = cursor.fetchall()
    up = values[0][0] if values else 0
    # if len(values) == 0:
    #     up = 0
    # else:
    #     up = values[0]['c']

    cursor.execute(
        'SELECT count(commited) c FROM m_cls where commited =0 and created_at = %s order by id desc limit 1',
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
