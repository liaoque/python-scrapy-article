from datetime import datetime

import scrapy
import json
from scrapy.loader import ItemLoader
import sys
import MySQLdb
import MySQLdb.cursors

import weixin.shares.items_date as SharesDateItems
import time


class Shares(scrapy.Spider):
    name = 'shares_date'
    allowed_domains = ['.eastmoney.com']
    start_urls = []
    headers = {
        "HOST": "push2his.eastmoney.com",
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
    }
    db = None
    cursor = None

    def get_url(self, code):
        # f11 - f20 买5
        # f31 - f40 卖5
        # f43 收盘
        # f44 最高
        # f45 最低
        # f46 开盘
        # f47 成交量
        # f48 成交额
        # f50 量比
        # f60 昨收
        # f84 总股本
        # f85 流通股
        # f86 时间戳
        # f92 净资本
        # f162 市盈率(动)
        # f163 市盈率(静态)
        # f164 市盈率(TTM)
        # f167 市净率
        # f168 换手率
        # f171 振幅
        # f57 股票代码
        # f58 名字
        # f105 净利润
        # f116 总市值
        # f117 流通市值
        # f135 主力流入
        # f136 主力流出
        # f137 主力净流入
        # f138 超大流入
        # f139 超大流出
        # f141 大流入
        # f142 大流出
        # f144 中单流入
        # f145 中单流出
        # f147 小单流入
        # f148 小单流出
        # f161 	内盘
        # f169  股价波动
        # f170  股价波动比例
        # f173  ROE
        return "https://push2.eastmoney.com/api/qt/stock/get?" \
               "ut=fa5fd1943c7b386f172d6893dbfba10b&fltt=2&invt=2&" \
               "fields=f120,f121,f122,f174,f175,f59,f163,f43,f57,f58,f169,f170,f46,f44,f51,f168,f47,f164,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,f135,f136,f137,f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f107,f111,f86,f177,f78,f110,f262,f263,f264,f267,f268,f255,f256,f257,f258,f127,f199,f128,f198,f259,f260,f261,f171,f277,f278,f279,f288,f152,f250,f251,f252,f253,f254,f269,f270,f271,f272,f273,f274,f275,f276,f265,f266,f289,f290,f286,f285,f292,f293,f294,f295" \
               "&secid=" + str(code) + "&cb=&_=1653740799012"

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

    def parse_content(self, response):
        result = json.loads(response.text)
        res = result["data"]
        item_loader = ItemLoader(item=SharesDateItems.Items())
        # 文档标题
        t = datetime.utcfromtimestamp(res["f86"])
        item_loader.add_value("name", res["f58"])
        item_loader.add_value("code", res["f57"])
        item_loader.add_value("p_min", res["f45"])
        item_loader.add_value("p_max", res["f44"])
        item_loader.add_value("p_start", res["f46"])
        item_loader.add_value("p_end", res["f43"])
        item_loader.add_value("p_range", res["f171"])
        item_loader.add_value("buy_count", res["f47"])
        item_loader.add_value("buy_sum", res["f48"])
        item_loader.add_value("master_buy_sum", res["f135"])
        item_loader.add_value("master_buy_sell", res["f136"])
        item_loader.add_value("date_as", t.strftime("%Y-%m-%d"))
        print(item_loader.load_item())
        # yield item_loader.load_item()
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
