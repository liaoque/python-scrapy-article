import scrapy
import json
from scrapy.loader import ItemLoader
import sys
import re
import MySQLdb
import MySQLdb.cursors

import weixin.shares.items as SharesItems
import time


class Shares_temper(scrapy.Spider):
    name = 'shares_temper'
    allowed_domains = ['.dfcfw.com']
    start_urls = []
    headers = {
        "HOST": "gubacdn.dfcfw.com"
    }

    def start_requests(self):
        db = MySQLdb.connect(host=self.settings.get('MYSQL_HOST'),
                             user=self.settings.get('MYSQL_USER'),
                             password=self.settings.get('MYSQL_PASSWORD'),
                             database=self.settings.get('MYSQL_DBNAME'),
                             charset='utf8mb4')
        # 使用cursor()方法获取操作游标
        cursor = db.cursor()
        sql = "update mc_shares_name set temper_dongfangcaifu = '0'  "
        cursor.execute(sql);
        sql = 'select code from mc_shares_name ';
        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 获取所有记录列表
            results = cursor.fetchall()
        except:
            print("Error: unable to fecth data")
        db.close()
        _list = []
        for url in results:
            # 替换url获取下载地址
            if int(url[0]) < 600000:
                _urtl = "http://gubacdn.dfcfw.com/LookUpAndDown/sz" + url[0] + ".js?_=" + str(time.time())
            else:
                _urtl = "http://gubacdn.dfcfw.com/LookUpAndDown/sh" + url[0] + ".js?_=" + str(time.time())
            self.headers['code'] = url[0]
            yield scrapy.Request(_urtl, headers=self.headers, callback=self.parse_content)
        pass

        pass

    def parse_content(self, response):

        LookUpAndDown = re.sub('var LookUpAndDown=', '', response.text)
        print(LookUpAndDown)
        result = json.loads(LookUpAndDown)
        code = response.request.headers.getlist('code')[0]

        # 文档标题
        item_loader = ItemLoader(item=SharesItems.Items())
        item_loader.add_value("code", code.decode(encoding = "utf-8"))
        item_loader.add_value("temper_dongfangcaifu", result["Data"]["TapeZ"] * 10000)

        return item_loader.load_item()

    pass
