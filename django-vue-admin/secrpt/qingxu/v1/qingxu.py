import sys
import os
import MySQLdb  # 修改为 MySQLdb
import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
# 设置根目录是secrpt
sys.path.insert(0, parent_dir)

from qingxu.v1 import dfcf, weibo, xueqiu, baidu
from qingxu.cls import cls
from common.database import getConfig


def compute():
    # print(parent_dir + '/mysql/v1/qingxu.db')
    mc = getConfig('mysql')
    conn = MySQLdb.connect(
        host=mc['host'],
        user=mc['user'],
        passwd=mc['passwd'],  # mysqlclient 使用 passwd 而不是 password
        db=mc['db'],
        init_command="SET time_zone = '+08:00'"  # 设置为东八区（北京时间）
    )
    cursor = conn.cursor()

    init(cursor)

    baidu.run(cursor)
    conn.commit()

    cls.run(cursor)
    conn.commit()

    weibo.run(cursor)
    conn.commit()

    # xueqiu.run(cursor)
    conn.commit()

    dfcf.run(cursor)


    # 提交事务:
    conn.commit()

    d = datetime.datetime.now().strftime('%Y-%m-%d')

    weight_cls = 0.27
    weight_weibo = 0.27
    weight_xueqiu = 0.27
    weight_dfcf = 0.07
    weight_shangzheng = 0.07
    weight_shangzhengzixun = 0.07

    cursor.close()
    conn.close()


def init(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS m_cls (
            id INT AUTO_INCREMENT PRIMARY KEY, 
            tid TEXT, 
            content TEXT, 
            created_at DATETIME, 
            type INT, 
            commited TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS m_weibo (
            id INT AUTO_INCREMENT PRIMARY KEY, 
            tid TEXT, 
            content TEXT, 
            created_at DATETIME, 
            type INT, 
            commited TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS m_xueqiu (
            id INT AUTO_INCREMENT PRIMARY KEY, 
            tid TEXT, 
            content TEXT, 
            created_at DATETIME, 
            type INT, 
            commited TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS m_dfcf (
            id INT AUTO_INCREMENT PRIMARY KEY, 
            tid TEXT, 
            kd_up TEXT, 
            kd_flat TEXT, 
            kd_down TEXT, 
            jg_up TEXT, 
            jg_flat TEXT, 
            jg_down TEXT, 
            cc_up TEXT, 
            cc_flat TEXT, 
            cc_down TEXT, 
            type INT, 
            created_at DATETIME
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS m_baidu (
            id INT AUTO_INCREMENT PRIMARY KEY, 
            zhishu TEXT, 
            zz_type INT, 
            created_at DATETIME
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS m_qingxu (
            id INT AUTO_INCREMENT PRIMARY KEY, 
            qingxu TEXT, 
            created_at DATETIME
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS m_qingxu_report (
            id INT AUTO_INCREMENT PRIMARY KEY, 
            table_name TEXT, 
            table_id INT, 
            isrun INT, 
            point INT, 
            created_at DATETIME
        )
    ''')
    pass


def queryMaxDate(cursor, yesterday):
    cursor.execute('SELECT id FROM m_qingxu where created_at = %s limit 1', (yesterday,))
    values = cursor.fetchall()
    if len(values) == 0:
        return None
    return values[0]


def queryRrport(cursor):
    cursor.execute('SELECT id FROM m_qingxu_report where isrun = 0 limit 20')
    values = cursor.fetchall()
    return values


if __name__ == "__main__":
    compute()
