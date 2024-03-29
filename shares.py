# -*- coding: utf-8 -*-

import re
import os
import time
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi
from datetime import datetime, date, timedelta

from urllib.request import urlopen
from urllib.request import Request

import configparser

cp = configparser.RawConfigParser()
cp.read("config.ini")
host = cp.get("db", "db_host")
database = cp.get("db", "db_database")
user = cp.get("db", "db_user")
password = cp.get("db", "db_pass")

db = MySQLdb.connect(host, user, password, database, charset='utf8mb4')
# 使用cursor()方法获取操作游标 
cursor = db.cursor()
sql = 'select code, name from mc_shares_name where code';
# 执行SQL语句
cursor.execute(sql)
date_as = time.strftime("%Y%m%d", time.localtime())
result = cursor.fetchall()

for item in result:
    code = item[0]
    name = item[1]

    # date_as = item['date_as']
    # sql = "SELECT id,date_as,p_p_range FROM mc_shares_zl  WHERE code = '%s' and date_as<='%s' order by date_as desc limit 5" % (
    #     code, date_as)

    sql = "SELECT ms.id, ms.date_as, mp. p_p_range FROM mc_shares ms" \
          " left join mc_shares_p_p_range mp on mp.share_id = ms.id " \
          "WHERE ms.code_id = '%s' and ms.date_as<='%s' order by ms.date_as desc limit 5" % (code, date_as)
    cursor.execute(sql)
    if cursor.rowcount == 0:
        continue
    result2 = cursor.fetchall()

    one = result2[0][1]
    one_p_range = result2[0][2]

    if len(result2) >= 2:
        two = result2[1][1]
        two_p_range = result2[1][2]
    else:
        two = one + timedelta(days=-1)
        two_p_range = 0
    pass

    if len(result2) >= 3:
        three = result2[2][1]
        three_p_range = result2[2][2]
    else:
        three = two + timedelta(days=-1)
        three_p_range = 0
    pass

    if len(result2) >= 4:
        four = result2[3][1]
        four_p_range = result2[3][2]
    else:
        four = three + timedelta(days=-1)
        four_p_range = 0
    pass

    if len(result2) >= 5:
        five = result2[4][1]
        five_p_range = result2[4][2]
    else:
        five = four + timedelta(days=-1)
        five_p_range = 0
    pass

    date_as = date_as

    sql = "SELECT id FROM mc_shares_last_three_day  WHERE code_id = '%s' and date_as='%s'" % (code, date_as)
    cursor.execute(sql)

    if cursor.rowcount:
        continue

    sql = """
        INSERT INTO mc_shares_last_three_day (name, code_id, one, one_p_range, two, two_p_range, three, three_p_range, four, four_p_range, five, five_p_range, date_as)
        VALUES (%s, %s, %s,  %s,  %s, %s, %s, %s,  %s,  %s,  %s,%s,  %s)
        """;
    params = (
        name,
        code,
        one,
        one_p_range,
        two,
        two_p_range,
        three,
        three_p_range,
        four,
        four_p_range,
        five,
        five_p_range,
        date_as
    )
    cursor.execute(sql, params)
    db.commit()
pass

db.close()
