# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.loader import ItemLoader
import sys

import time
import MySQLdb
import MySQLdb.cursors


# import baozouribao.items

# from scrapy.spiders import CrawlSpider, Rule
# from scrapy.linkextractors import LinkExtractor

class SharesFh(scrapy.Spider):
    name = 'shares_fh'

    allowed_domains = ['.10jqka.com.cn']
    start_urls = []
    headers = {
        "HOST": "basic.10jqka.com.cn",
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
    }
    db = None
    cursor = None

    def get_url(self, code):
        return 'http://basic.10jqka.com.cn/' + str(code) + '/bonus.html#stockpage'

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
            yield scrapy.Request(url,
                                 headers=self.headers,
                                 dont_filter=True,
                                 callback=self.parse)

    def parse(self, response):
        itemList = response.css("#bonus_table tbody tr");
        for item in itemList:
            thumbnail = item.css("td")[0]
            print(thumbnail.extract_first())
            break
            # desc = item.css(".j-r-list-c .j-r-list-c-desc a::text").extract_first();
        #     title = item.css(".j-r-list-tool::attr(data-title)").extract_first();
        #     if desc:
        #         desc = '<p>' + desc + '</p>'
        #     if thumbnail:
        #         src = '<p><img src=' + thumbnail + ' /></p>'
        #         yield self.parse_content({
        #             'body': '<div class="content">' + desc + src + '</div>',
        #             'src': thumbnail,
        #             'type': type,
        #             'thumbnail': thumbnail,
        #             'title': title,
        #         });
        #
        #
        #
        #
        # for key, item in enumerate(items):
        #     yield self.parse_content({
        #         'body': item,
        #         'src': item,
        #         'type': type,
        #         'thumbnail': itemsThumbnail[key],
        #         'title': itemTitles[key],
        #     })

        pass

    def parse_content(self, item):
        # article = item;
        # item_loader = ItemLoader(item=BaiSiBuDeJieItem.Items())
        # # 缩略图
        # item_loader.add_value("thumbnail", article.get("thumbnail", 0))
        # item_loader.add_value("src", article.get("src", 0))
        # # 文档标题
        # item_loader.add_value("title", article.get("title", 0))
        # item_loader.add_value("title", article.get("title", 0))
        # # content
        # item_loader.add_value("body", article.get("body", ''))
        # # 文档URL
        # item_loader.add_value("type", article.get("type", ''))
        # return item_loader.load_item()
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
