import sys
import os
import sqlite3
import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
# 设置根目录是secrpt
sys.path.insert(0, parent_dir)


from qingxu.ths.wencai import jijinTop10All

def saveStock(cursor, s, type):
    codes = jijinTop10All("所属上证50基金, 100日涨跌幅，排除c类基金")
    for (code, num) in codes:
        cursor.execute('insert into m_stock (code , num , type , created_at )values(?,?,?,?)',
                       code, num, str(type), datetime.datetime.now().strftime('%Y-%m-%d'))

def compute():
    conn = sqlite3.connect('qingxu2.db')
    conn.row_factory = sqlite3.Row
    # 创建一个Cursor:
    cursor = conn.cursor()
    res = init(cursor)
    if res:
        saveStock(cursor, "所属上证50基金, 100日涨跌幅，排除c类基金", "50")
        saveStock(cursor, "所属上证50基金, 所属沪深300基金，排除c类基金", "300")
        saveStock(cursor, "所属上证50基金, 所属中证500基金，排除c类基金", "500")
        saveStock(cursor, "所属上证50基金, 所属中证1000基金，排除c类基金", "1000")
        saveStock(cursor, "所属上证50基金, 同花顺主题分类是科创板，排除c类基金", "kc")

    # 查股票
    # 根据股票查雪球

    # 关闭Cursor:
    cursor.close()
    conn.close()


def init(cursor):
    # code 股票代码， num 基金选中的数量， type 50，300，500， 1000， kc
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS m_stock (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, code TEXT, num integer, type TEXT, created_at TEXT)')
    # cursor.execute(
    #     'CREATE TABLE IF NOT EXISTS m_xueqiu (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, tid TEXT, content TEXT, created_at TEXT, type integer, commited TEXT)')

    if isInit(cursor):
        cursor.execute('delete from m_stock')
        return  True
    return  False


def isInit(cursor):
    """
    没有数据或者 时间不对的，删除重新初始化股票
    :param cursor:
    :return:
    """
    cursor.execute('SELECT id FROM m_stock limit 1')
    values = cursor.fetchall()
    if len(values) == 0:
        return True
    return values[0]['created_at'] == datetime.datetime.now().strftime('%Y-%m-%d')

def queryMaxDate(cursor, yesterday):
    cursor.execute('SELECT id FROM m_qingxu where  created_at = ? limit 1', (yesterday))
    values = cursor.fetchall()
    if len(values) == 0:
        return None
    return values[0]


if __name__ == "__main__":
    compute()
