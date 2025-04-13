# 羊毛
import sys
import os
import sqlite3
import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
# 设置根目录是secrpt
sys.path.insert(0, parent_dir)

from qingxu.weibo.container import fetch_weibo_container
from common import dingding


# 关键字
keywords = ["如有点亮满足天数"]


def init(cursor):
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS m_ym (id integer NOT NULL PRIMARY KEY AUTOINCREMENT,weiboid TEXT,  containerid TEXT, content TEXT, created_at TEXT, type integer, `scheme` TEXT)')
    pass


def saveStock(cursor, weibos):
    for item in weibos:
        cursor.execute('SELECT id FROM m_ym where content = ?', (item['content'],))
        values = cursor.fetchall()
        if len(values) == 0:
            cursor.execute(
                'insert into m_ym (weiboid, containerid,content,type,created_at,scheme)values(?,?,?,?,?,?)',
                (item['weiboid'], item['containerid'], item['content'], 1, item['created_at'], item['scheme'])
            )
            for keyword in keywords:
                if keyword in item['content']:
                    dingding.dingding("找到包含 %s  ： %s" % (keyword, item['content']))


def compute():
    conn = sqlite3.connect('ym.db', isolation_level=None)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    init(cursor)

    # 小屁屁挖白菜
    params = {
        "containerid": "2304133194506490",
        "page_type": "03",
        "since_id": "",
    }
    result = fetch_weibo_container(params)
    saveStock(cursor, result)

    # 小屁屁找
    params = {
        "containerid": "2304135748988380",
        "page_type": "03",
        "since_id": "",
    }
    result = fetch_weibo_container(params)
    saveStock(cursor, result)

    # 披着羊毛的魔鬼
    params = {
        "containerid": "2304131917872472",
        "page_type": "03",
        "since_id": "",
    }
    result = fetch_weibo_container(params)
    saveStock(cursor, result)

    # 薅羊毛大队长
    params = {
        "containerid": "2304135069029750",
        "page_type": "03",
        "since_id": "",
    }
    result = fetch_weibo_container(params)
    saveStock(cursor, result)

    cursor.close()
    conn.close()


if __name__ == "__main__":
    compute()
