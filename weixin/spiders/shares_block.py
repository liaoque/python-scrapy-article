# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.loader import ItemLoader
import sys

import time
import MySQLdb
import MySQLdb.cursors
import weixin.shares.items_fh as SharesFhItems
import copy


# import baozouribao.items

# from scrapy.spiders import CrawlSpider, Rule
# from scrapy.linkextractors import LinkExtractor

class SharesBlock(scrapy.Spider):
    name = 'shares_block'

    allowed_domains = ['.10jqka.com.cn']
    start_urls = []
    headers = {
        "HOST": "basic.10jqka.com.cn",
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
    }
    db = None
    cursor = None

    def get_url(self, code):
        return 'http://basic.10jqka.com.cn/' + str(code) + '/concept.html'

    def connect(self):
        if self.db == None:
            self.db = MySQLdb.connect(host=self.settings.get('MYSQL_HOST'),
                                      user=self.settings.get('MYSQL_USER'),
                                      password=self.settings.get('MYSQL_PASSWORD'),
                                      database=self.settings.get('MYSQL_DBNAME'),
                                      charset='utf8mb4')
            self.cursor = self.db.cursor()

    def start_requests(self):
        self.connect()
        results = self.findStoks()
        for item in results:
            code = item[0]

            url = self.get_url(code)
            headers = copy.deepcopy(self.headers)
            headers['code'] = code
            yield scrapy.Request(url,
                                 headers=headers,
                                 dont_filter=True,
                                 callback=self.parse)
            break

    def parse(self, response):
        code = response.request.headers.getlist('code')[0].decode("UTF-8")
        itemList = response.css(".gnContent tbody tr .gnName")
        # print(itemList)
        for item in itemList:
            name = item.text()
            code = item.attr("cid::text")
            print(name,code)


        itemList = response.css(".gnContent tbody tr .gnStockList");
        for item in itemList:
            print(item)

        # all = item.css(".gnName::text")
        # if len(all) > 0:
        #     yield self.parse_content(all, code)
        # all = item.css(".gnStockList::text").getall()
        # if len(all) > 0:
        #     yield self.parse_content(all, code)
        pass

    def parse_content(self, item, code):
        item_loader = ItemLoader(item=SharesFhItems.Items())
        for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            if item[i] == '--':
                item[i] = None
        item_loader.add_value("code", code)
        item_loader.add_value("title", item[0])
        item_loader.add_value("info", item[4])
        item_loader.add_value("amount", item[7])
        item_loader.add_value("range", item[9])
        item_loader.add_value("directors_date_as", item[1])
        item_loader.add_value("shareholder_date_as", item[2])
        item_loader.add_value("implement_date_as", item[3])
        item_loader.add_value("register_date_as", item[5])
        item_loader.add_value("ex_date_as", item[6])
        return item_loader.load_item()
        pass

    def findStoks(self):
        sql = 'select code,name,area_id from mc_shares_name where status = 1 and code_type =1';
        results = []
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 获取所有记录列表
            results = self.cursor.fetchall()
        except:
            print("Error: unable to fecth data")
        return results

    def __del__(self):
        if self.db != None:
            self.cursor.close()
            self.db.close()
