import scrapy
import json
import sys
import re

from datetime import datetime
import copy
import MySQLdb
import MySQLdb.cursors

from scrapy.loader import ItemLoader
import weixin.shares.items_ban as SharesItems

class Shares_ban(scrapy.Spider):
    name = 'shares_ban'
    total = 1
    allowed_domains = ['.10jqka.com.cn']
    start_urls = []
    headers = {
        "HOST": "q.10jqka.com.cn"
    }
    db = None
    cursor = None

    def start_requests(self):
        db = MySQLdb.connect(host=self.settings.get('MYSQL_HOST'),
                             user=self.settings.get('MYSQL_USER'),
                             password=self.settings.get('MYSQL_PASSWORD'),
                             database=self.settings.get('MYSQL_DBNAME'),
                             charset='utf8mb4')
        cursor = db.cursor()
        sql = 'delete from mc_shares_ban where date_as < %s ';
        try:
            import datetime
            today = datetime.datetime.today()
            yesterday = today - datetime.timedelta(days=15)
            # 执行SQL语句
            cursor.execute(sql, (
                yesterday.date().strftime('%Y-%m-%d')
            ))
            db.commit()
        except:
            print("Error: unable to fecth data")
            db.rollback()

        url="http://ai.10jqka.com.cn/transfer/transfer/get?unique=1&allfields=0&websource=1"
        yield scrapy.Request(url,  callback=self.parse, dont_filter=True)

    def parse(self, response):
        result = json.loads(response.text)

        #         avoid_cycle: 3
        # avoid_reason: "股份冻结"
        # ctime: "2021-12-23 00:22:22"
        # market: 33
        # remain_avoid_cycle: 2
        # stock: "000159"
        # stock_name: "国际实业"
        for item in result["result"]:
            print(item)
            item_loader = ItemLoader(item=SharesItems.Items())
            item_loader.add_value("code", item['stock'])
            item_loader.add_value("avoid_cycle", item['avoid_cycle'])
            item_loader.add_value("remain_avoid_cycle", item['remain_avoid_cycle'])
            item_loader.add_value("avoid_reason", item['avoid_reason'])
            item_loader.add_value("date_as", item['ctime'])
            yield item_loader.load_item()

        pass

    def __del__(self):
        if self.db != None:
            self.cursor.close()
            self.db.close()