import sys
import os
import sqlite3
import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
# 设置根目录是secrpt
sys.path.insert(0, parent_dir)


from qingxu import cls,dfcf,weibo,xueqiu,baidu,gpt


def compute():

    conn = sqlite3.connect('qingxu.db')
    conn.row_factory = sqlite3.Row
    # 创建一个Cursor:
    cursor = conn.cursor()


    init(cursor)

    cls.run(cursor)
    weibo.run(cursor)
    xueqiu.run(cursor)

    dfcf.run(cursor)
    baidu.run(cursor)


    # 提交事务:
    conn.commit()

    gpt.run(cursor)
    conn.commit()

    # trend_shangzheng, trend_shangzhengzixun = baidu.run(cursor)

    d = datetime.datetime.now().strftime('%Y-%m-%d')

    weight_cls = 0.27
    weight_weibo = 0.27
    weight_xueqiu = 0.27
    weight_dfcf = 0.07
    weight_shangzheng = 0.07
    weight_shangzhengzixun = 0.07

    # cls_sentiment = cls.queryCommitPoint(cursor, d)
    # weibo_sentiment = weibo.queryCommitPoint(cursor, d)
    # xueqiu_sentiment = xueqiu.queryCommitPoint(cursor, d)
    # dfcf_sentiment = dfcf.queryCommitPoint(cursor, d)

    #
    # sentiment_index = (weight_weibo * weibo_sentiment) + (
    #         cls_sentiment * weight_cls) + (
    #                           xueqiu_sentiment * weight_xueqiu) + (
    #                           dfcf_sentiment * weight_trend) + (
    #                           trend_shangzheng * weight_trend) + (
    #                           trend_shangzhengzixun * weight_xueqiu)
    # print(f"当前股票情绪指数为：{sentiment_index}")



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
        'CREATE TABLE IF NOT EXISTS m_baidu (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, shangzheng TEXT, shangzhengzixun TEXT, created_at TEXT)')
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
