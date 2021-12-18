import scrapy
import json
from scrapy.loader import ItemLoader
import sys
import MySQLdb
import MySQLdb.cursors

import weixin.shares.items_date as SharesDateItems
import time


class Shares(scrapy.Spider):
    name = 'shares'
    allowed_domains = ['.eastmoney.com']
    start_urls = []
    headers = {
        "HOST": "push2.eastmoney.com"
    }
    db = None
    cursor = None

    def get_url(self, code):
        return 'https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=' + \
               str(code) + '&cb=&klt=101&fqt=0&lmt=1000000&end=20500101&iscca=1&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58'

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.db = MySQLdb.connect(host=self.settings.get('MYSQL_HOST'),
                             user=self.settings.get('MYSQL_USER'),
                             password=self.settings.get('MYSQL_PASSWORD'),
                             database=self.settings.get('MYSQL_DBNAME'),
                             charset='utf8mb4')
        self.cursor = self.db.cursor()


    # http://11.push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152&_=1584074266443"
    def start_requests(self):
        results = self.findStoks()
        for item in results:
            code = item[0]

            stock_info = self.findStokByCode(code)
            print(stock_info)
            return

            area_id = item[2]
            if area_id == 1:
                s_code = "1." + code
            else:
                s_code = "0." + code
            url = self.get_url(s_code)
            yield scrapy.Request(url,
                                 headers=self.headers,
                                 dont_filter=True,
                                 callback=self.parse_content)
        pass

    def parse_content(self, response):
        result = json.loads(response.text)
        # print(result["data"]["klines"])
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
            item_loader.add_value("p_range", res[7])
            item_loader.add_value("buy_count", res[5])
            item_loader.add_value("buy_sum", res[6])
            item_loader.add_value("date_as", res[0])
            yield item_loader.load_item()
        pass

    def findStoks(self):
        sql = 'select code,name,area_id from mc_shares_name';
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
        sql = 'SELECT code,name,date_as FROM `mc_shares` WHERE CODE = %s ORDER BY date_as DESC LIMIT 1'%(code);
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
        self.cursor.close()
        self.db.close()
