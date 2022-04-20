from datetime import datetime

import scrapy
import json
from scrapy.loader import ItemLoader
import sys
import MySQLdb
import MySQLdb.cursors

import weixin.shares.items_hours as SharesDateItems
import time


class Shares(scrapy.Spider):
    name = 'shares_hours'
    allowed_domains = ['.eastmoney.com']
    start_urls = []
    headers = {
        "HOST": "push2his.eastmoney.com",
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
    }
    db = None
    cursor = None

    # https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55&ut=7eea3edcaed734bea9cbfc24409ed989&klt=60&fqt=0&secid=0.000001&beg=0&end=20500000&_=1650443713203
    def get_url(self, code, days):
        if days <= 0:
            days = 100000
        return 'https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=' + \
               str(code) + '&cb=&klt=60&fqt=0&lmt=' + str(days) + \
               '&end=20500101&iscca=1&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55'

    def connect(self):
        if self.db == None:
            self.db = MySQLdb.connect(host=self.settings.get('MYSQL_HOST'),
                                      user=self.settings.get('MYSQL_USER'),
                                      password=self.settings.get('MYSQL_PASSWORD'),
                                      database=self.settings.get('MYSQL_DBNAME'),
                                      charset='utf8mb4')
            self.cursor = self.db.cursor()

    # http://11.push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152&_=1584074266443"
    def start_requests(self):
        self.connect()
        results = self.findStoks()
        for item in results:
            code = item[0]
            days = 0

            stock_info = self.findStokByCode(code)
            if stock_info:
                days = (datetime.now().date() - stock_info[2]).days
                if days < 1:
                    continue
            area_id = item[2]
            if area_id == 1:
                s_code = "1." + code
            else:
                s_code = "0." + code
            url = self.get_url(s_code, days)
            yield scrapy.Request(url,
                                 headers=self.headers,
                                 dont_filter=True,
                                 callback=self.parse_content)

    def parse_content(self, response):
        result = json.loads(response.text)
        # title = response.css('span a::text').extract_first();
        # url = response.css('span a::attr(href)').extract_first();
        # img = response.css('img::attr(src)').extract_first();
        # text_type = response.css('.h70 .fl_l::text').extract_first();
        for item in result["data"]["klines"]:
            res = item.split(',')
            item_loader = ItemLoader(item=SharesDateItems.Items())

            # 文档标题
            item_loader.add_value("name", result["data"]["name"])
            item_loader.add_value("code", result["data"]["code"])
            item_loader.add_value("p_min", res[4])
            item_loader.add_value("p_max", res[3])
            item_loader.add_value("p_start", res[1])
            item_loader.add_value("p_end", res[2])
            item_loader.add_value("date_as", res[0])
            yield item_loader.load_item()
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

    def findStokByCode(self, code):
        sql = "SELECT code_id as code,name,date_as FROM `mc_shares_hours` WHERE code_id = '%s' ORDER BY date_as DESC LIMIT 1" % (code);
        results = []
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 获取所有记录列表
            results = self.cursor.fetchone()
        except:
            print("Error: unable to fecth data")
        return results

    def __del__(self):
        if self.db != None:
            self.cursor.close()
            self.db.close()
