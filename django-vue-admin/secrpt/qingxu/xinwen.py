import sys
import os
import sqlite3

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
# 设置根目录是secrpt
sys.path.insert(0, parent_dir)


from qingxu import cls
from qingxu.v1 import baidu,dfcf,weibo,xueqiu


def compute():

    conn = sqlite3.connect(parent_dir + '/sqlitefile/v1/qingxu.db', isolation_level=None)
    conn.row_factory = sqlite3.Row
    # 创建一个Cursor:
    cursor = conn.cursor()


    init(cursor)

    cls.run(cursor)
    weibo.run(cursor)
    xueqiu.run(cursor)

    dfcf.run(cursor)
    baidu.run(cursor)


    # 关闭Cursor:
    cursor.close()
    conn.close()


def init(cursor):
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS m_cls (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, tid TEXT, content TEXT, created_at TEXT, type integer, `commited` TEXT)')
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS m_weibo (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, tid TEXT, content TEXT, created_at TEXT, type integer, commited TEXT)')
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS m_xueqiu (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, tid TEXT, content TEXT, created_at TEXT, type integer, commited TEXT)')
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS m_dfcf (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, tid TEXT, kd_up TEXT, kd_flat TEXT, kd_down TEXT, jg_up TEXT, jg_flat TEXT, jg_down TEXT, cc_up TEXT, cc_flat TEXT, cc_down TEXT,type integer, created_at TEXT)')
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS m_baidu (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, zhishu TEXT, zz_type integer , created_at TEXT)')

    cursor.execute(
        'CREATE TABLE IF NOT EXISTS m_qingxu (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, qingxu TEXT,  created_at TEXT)')
    pass


def queryMaxDate(cursor, yesterday):
    cursor.execute('SELECT id FROM m_qingxu where  created_at = ? limit 1', (yesterday))
    values = cursor.fetchall()
    if len(values) == 0:
        return None
    return values[0]


if __name__ == "__main__":
    compute()
