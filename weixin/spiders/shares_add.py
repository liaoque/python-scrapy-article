import scrapy
import json
import sys
import re

from datetime import datetime
import copy
import MySQLdb
import MySQLdb.cursors

class Shares_add(scrapy.Spider):
    name = 'shares_add'
    total = 1
    allowed_domains = ['.10jqka.com.cn']
    start_urls = []
    headers = {
        "HOST": "q.10jqka.com.cn"
    }
    db = None
    cursor = None

    def connect(self):
        if self.db == None:
            self.db = MySQLdb.connect(host=self.settings.get('MYSQL_HOST'),
                                      user=self.settings.get('MYSQL_USER'),
                                      password=self.settings.get('MYSQL_PASSWORD'),
                                      database=self.settings.get('MYSQL_DBNAME'),
                                      charset='utf8mb4')
            self.cursor = self.db.cursor()

    def get_url(self, code):
        # http://q.10jqka.com.cn/api.php?t=myStocks&op=add&stockcode=300148
        return "http://q.10jqka.com.cn/api.php?t=myStocks&op=add&stockcode=" + code

    # http://11.push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152&_=1584074266443"
    def start_requests(self):
        self.connect()
        results = self.findStoks()

        for item in results:
            code = item[0]
            self.init_area_request(code)


    def init_area_request(self, code):
        headers = copy.deepcopy(self.headers)
        headers['hexin-v'] = self.settings.get('TONG_HEXIN')
        url = self.get_url(code)
        coo = self.settings.get('TONG_COOKIE')
        print(url, coo, headers)
        return scrapy.Request(url, cookies=coo, headers=headers, callback=self.parse, dont_filter=True)

    def parse(self, response):
        pass



    def findStoks(self):
        today = datetime.now().date().strftime('%Y-%m-%d')
        today = '2021-12-22'
        sql = 'SELECT code_id FROM `mc_shares_kdj` where j < 0 and (code_id < 300000 or code_id > 400000) and date_as=\'%s\''%(today);
        results = []
        try:
            print(sql)
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