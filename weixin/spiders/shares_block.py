# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.loader import ItemLoader
import sys
import re

import time
import MySQLdb
import MySQLdb.cursors
import weixin.shares.items as SharesItems
import weixin.shares.items_block as SharesItemsBlock
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

    # http://basic.10jqka.com.cn/000615/position.html
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
            time.sleep(10)


    def parse(self, response):
        code = response.request.headers.getlist('code')[0].decode("UTF-8")
        itemList = response.css(".gnContent tbody tr .gnName")
        # print(itemList)
        for item in itemList:
            block_name = re.sub(r"\s+", "", item.css("::text").get())
            block_code = re.sub(r"\s+", "", item.css("::attr(clid)").get())
            # yield self.parse_content(block_name, block_code)
            yield self.parse_content2(block_code, code)

        itemList = response.css(".gnContent tbody tr .gnStockList");
        for item in itemList:
            block_name = re.sub(r"\s+", "", item.css("::text").get())
            block_code = re.sub(r"\s+", "", item.css("::attr(cid)").get())
            # yield self.parse_content(block_name, block_code)
            yield self.parse_content2(block_code, code)
        pass

    def parse_content(self, block_name, block_code):
        print("加入板块：%s" % (block_name))
        item_loader = ItemLoader(item=SharesItems.Items())
        item_loader.add_value("code", block_code)
        item_loader.add_value("name", block_name)
        item_loader.add_value("area_id", '90')
        item_loader.add_value("status", '1')
        item_loader.add_value("code_type", '4')
        item_loader.add_value("pe", '0')
        item_loader.add_value("pb", '0')
        return item_loader.load_item()

    def parse_content2(self, block_code, code_id):
        item_loader2 = ItemLoader(item=SharesItemsBlock.Items())
        item_loader2.add_value("code_id", code_id)
        item_loader2.add_value("block_code_id", block_code)
        item_loader2.add_value("code_type", 2)
        return item_loader2.load_item()

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