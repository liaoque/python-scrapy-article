import scrapy
import json

from scrapy.loader import ItemLoader
import weixin.shares.items_industry_date as SharesIndustyDateItems
import time
import copy
import MySQLdb
import MySQLdb.cursors
import time
from datetime import datetime


# http://zx.10jqka.com.cn/indval/getallindustry
# https://www.liujiangblog.com/course/django/88
class Shares_industry_date(scrapy.Spider):
    name = 'shares_industry_date'
    total = 1
    allowed_domains = ['.eastmoney.com']
    start_urls = []
    area_map = {
        "SH": "m:1+t:2,m:1+t:23",
        "SZ": "m:0+t:6,m:0+t:80",
        "BJ": "m:0+t:81+s:2048",
    }
    headers = {
        "HOST": "24.push2his.eastmoney.com"
    }
    db = None
    cursor = None

    def get_url(self, industry, days):
        if days <= 0:
            days = 100000
        return "https://24.push2his.eastmoney.com/api/qt/stock/kline/get?cb=&" \
               "secid=90." + str(industry) + "&ut=fa5fd1943c7b386f172d6893dbfba10b&" \
                                             "fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&" \
                                             "klt=101&fqt=1&beg=0&end=20500101&smplmt=755&lmt=" + str(
            days) + "&_=1641017528891"

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
        results = self.findIndustry()

        for item in results:
            code = item[0]
            days = 0
            stock_info = self.findIndustryByCode(code)
            if stock_info:
                days = (datetime.now().date() - stock_info[1]).days
                if days < 1:
                    return
            url = self.get_url(code, days)
            yield scrapy.Request(url,
                                 headers=self.headers,
                                 dont_filter=True,
                                 callback=self.parse_content)

    def parse_content(self, response):
        result = json.loads(response.text)
        # print(result)
        for item in result["data"]["klines"]:
            res = item.split(',')
            item_loader = ItemLoader(item=SharesIndustyDateItems.Items())
            # 文档标题
            item_loader.add_value("code", result["data"]["code"])
            item_loader.add_value("p_min", res[4])
            item_loader.add_value("p_max", res[3])
            item_loader.add_value("p_start", res[1])
            item_loader.add_value("p_end", res[2])
            item_loader.add_value("date_as", res[0])
            item_loader.add_value("p_rate", res[8])
            yield item_loader.load_item()

    def findIndustry(self):
        sql = 'select code,name from mc_shares_name where code_type = 2';
        results = []
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 获取所有记录列表
            results = self.cursor.fetchall()
        except:
            print("Error: unable to fecth data")
        return results

    def findIndustryByCode(self, code):
        sql = "SELECT code_id as code,date_as " \
              "FROM `mc_shares_industry`" \
              " WHERE code_id = '%s' ORDER BY date_as DESC LIMIT 1" % (
                  code);
        results = []
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 获取所有记录列表
            results = self.cursor.fetchone()
        except:
            print("Error: unable to fecth data")
        return results
