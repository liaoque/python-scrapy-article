# -*- coding: utf-8 -*-
import configparser
import re
import os
import time
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi
from datetime import datetime, date, timedelta

from urllib.request import urlopen
from urllib.request import Request

cp = configparser.ConfigParser()
cp.read("config.ini")
host = cp.get("db", "db_host")
database = cp.get("db", "db_database")
user = cp.get("db", "db_user")
password = cp.get("db", "db_pass")

db = MySQLdb.connect(host, user, password, database, charset='utf8mb4')
# 使用cursor()方法获取操作游标 
cursor = db.cursor()

sql = 'select id from mc_shares_p_p_range where share_id in (select max(id) from mc_shares) '
cursor.execute(sql)
if cursor.rowcount == 0:
    sql = 'insert into mc_shares_p_p_range(share_id, p_end, min_end, p_p_range)select id, p_end, min(p_end) as p_p_end, (min(p_end) - p_end) / p_end * 10000 from mc_shares group by code order by date_as desc '
    cursor.execute(sql)


db.commit()


# 整理数据
# sql = 'select date_as from mc_shares_zl order by date_as desc limit 1';
# cursor.execute(sql)
# if cursor.rowcount:
#     result2 = cursor.fetchall()
#     date_as = result2[0]['date_as']
#     # 找到最新的时间的数据
#     sql = "select name, code, p_min, p_max, p_start, p_end, p_range, buy_count, buy_sum, date_as from mc_shares where date_as >= '%s' order by date_as asc" % (
#         date_as)
# else:
#     sql = "select name, code, p_min, p_max, p_start, p_end, p_range, buy_count, buy_sum, date_as from mc_shares order by date_as asc"
# pass
# cursor.execute(sql)
# if cursor.rowcount:
#     result2 = cursor.fetchall()
#     for res in result2:
#         p_p_range = 0
#         # 查找最后的一天的p_end
#         sql = "SELECT p_end FROM mc_shares WHERE code = '%s' and date_as < '%s' order by date_as desc limit 1" % (
#             res[1], res[9])
#
#         cursor.execute(sql)
#         if cursor.rowcount:
#             result3 = cursor.fetchall()
#             old_p_end = result3[0][0]
#             p_p_range = int((res[5] - old_p_end) / old_p_end * 10000)
#         pass
#         sql = """
#             INSERT INTO mc_shares_zl (name, code, p_min, p_max, p_start, p_end, p_range, buy_count, buy_sum, date_as, p_p_range)
#             VALUES (%s, %s, %s,  %s,  %s, %s, %s, %s, %s, %s,  %s)
#             """
#         params = res + (p_p_range,)
#         cursor.execute(sql, params)
#         db.commit()
#     pass
# pass

db.close()
