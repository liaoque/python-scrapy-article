# -*- coding: utf-8 -*-

import re
import os
import time
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi

from urllib.request import urlopen
from urllib.request import Request


host = "192.168.16.248"
database = "article_spider"
user = "root"
password = "123456"


db = MySQLdb.connect(host,user,password,database, charset='utf8mb4' )
# 使用cursor()方法获取操作游标 
cursor = db.cursor()
sql = 'select count(1) as c from mc_6m5m where status = 200';
# 执行SQL语句
cursor.execute(sql)
# 获取所有记录列表
data = cursor.fetchone()
i = 0
n = data[0]
baseUrl = 'http://down001.6m5m.com'
basePath = 'F:/360Downloads'

print("共%s条数据"%(n,))
c = 0;
while i < n:
    i = i +1
    sql = 'select id, zip_url from mc_6m5m where status = 200 and down_status = 0 limit 1';
    cursor.execute(sql)
    if cursor.rowcount < 1:
        break

    # 获取所有记录列表
    data = cursor.fetchone()
    if data[1] == '#file':
        continue
        pass
    id = data[0]
    file = re.sub('#file', '', data[1])
    url = baseUrl + '/' + data[1]

    file = basePath + '/' + file
    path = os.path.dirname(file)
    if not os.path.exists(path):
        os.makedirs(path)

    try:
        print("获取下载文件",url)
        response = urlopen(url)
        fileContent = response.read()
        # 文件存储
        with open(file,'wb') as f:
            f.write(fileContent)
            pass
        pass
        print( "下载成功 %s",file )
        sql = 'update mc_6m5m set down_status = 200 where id = %s' % (id,);
        
        cursor.execute(sql)
        db.commit()
        c = c + 1
        time.sleep(1)
    except BaseException:
        print("下载失败",url)
        sql = 'update article_spider.mc_6m5m set down_status = 400 where id = 22' ;
        res = cursor.execute(sql)
        db.commit()
        time.sleep(5)
    else:
        print("下载结束")


db.close()
