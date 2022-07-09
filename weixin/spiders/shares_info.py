import copy
from datetime import datetime

import scrapy
import json
from scrapy.loader import ItemLoader
import sys
import MySQLdb
import MySQLdb.cursors

import weixin.shares.items_info as SharesInfoItems
import time


class Shares(scrapy.Spider):
    name = 'shares_info'
    # allowed_domains = ['.10jqka.com.cn']
    allowed_domains = ['.eastmoney.com', '.10jqka.com.cn']
    # start_urls = []
    headers = {
        "HOST": "push2his.eastmoney.com",
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
    }
    db = None
    cursor = None

    def get_url(self, code):
        # 股票 0
        # f9市盈率(动)
        # f12 股票代码
        # f23 市净率
        # f37 ROE
        # f49 毛利率
        # f129 净利率

        # 行业 1
        # f9市盈率(动)
        # f12 股票代码
        # f23 市净率
        # f37 ROE
        # f49 毛利率
        # f129 净利率
        return "https://push2.eastmoney.com/api/qt/slist/get?" \
               "spt=1&np=3&fltt=2&invt=2&fields=f9,f12,f13,f14,f20,f23,f37,f45,f49,f134,f135,f129,f1000,f2000,f3000&" \
               "ut=bd1d9ddb04089700cf9c27f6f7426281&cb=&secid=" + str(code) + "&_=1654060484482"

    def get_url2(self, code):
        return "https://push2.eastmoney.com/api/qt/stock/get?ut=" \
               "&fltt=2&invt=2&fields=f57,f164,f163&secid=" + str(code) + "&wbp2u=5204545223982760|0|1|0|web&cb=&_=1657375827577"

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
            # headers = copy.deepcopy(self.headers)
            # yield scrapy.Request(url,
            #                      headers=headers,
            #                      dont_filter=True,
            #                      callback=self.parse_content)

            url = self.get_url2(s_code)
            headers = copy.deepcopy(self.headers)
            yield scrapy.Request(url,
                                 headers=headers,
                                 dont_filter=True,
                                 callback=self.parse_content2)


        # for item in results:
        #     yield self.request_info(item)
        #     time.sleep(5)

    def request_info(self, item):
        code = item[0]
        industry_code = item[3]
        if code > '700000':
            return
        headers = copy.deepcopy(self.headers)
        headers['HOST'] = "doctor.10jqka.com.cn"
        headers['code'] = code
        headers['industry_code'] = industry_code
        url = "http://doctor.10jqka.com.cn/" + str(code) + "/#nav_basic"
        return scrapy.Request(url,
                              headers=headers,
                              dont_filter=True,
                              callback=self.parse_content_info)

    def parse_content_info(self, response):
        code = response.request.headers.getlist('code')[0].decode("UTF-8")
        industry_code = response.request.headers.getlist('industry_code')[0].decode("UTF-8")

        yysrzzl = response.css("#yysrzzl  tr")
        jlrzzl = response.css("#jlrzzl  tr")

        gpm_ex = yysrzzl[1].css("td")[1].css("::text").get()
        npmos_ex = jlrzzl[1].css("td")[1].css("::text").get()
        item_loader2 = ItemLoader(item=SharesInfoItems.Items())
        item_loader2.add_value("code", code)
        item_loader2.add_value("gpm_ex", float(gpm_ex) * 100)
        item_loader2.add_value("npmos_ex", float(npmos_ex) * 100)
        item_loader2.add_value("type", 'gpm_ex')
        # print(item_loader2.load_item())
        yield item_loader2.load_item()

        gpm_ex = yysrzzl[2].css("td")[1].css("::text").get()
        npmos_ex = jlrzzl[2].css("td")[1].css("::text").get()
        item_loader3 = ItemLoader(item=SharesInfoItems.Items())
        item_loader3.add_value("code", industry_code)
        item_loader3.add_value("gpm_ex", float(gpm_ex) * 100)
        item_loader3.add_value("npmos_ex", float(npmos_ex) * 100)
        item_loader3.add_value("type", 'gpm_ex')
        yield item_loader3.load_item()

        pass

    def parse_content(self, response):
        result = json.loads(response.text)
        if "data" not in result:
            return
        if result["data"] is None or "diff" not in result["data"]:
            return

        res = result["data"]["diff"][0]
        item_loader2 = ItemLoader(item=SharesInfoItems.Items())
        item_loader2.add_value("code", res["f12"])
        item_loader2.add_value("pb", float(res["f23"]) * 100)
        # item_loader2.add_value("pe", res["f9"])
        item_loader2.add_value("pe_d", float(res["f9"]) * 100)
        # item_loader2.add_value("pe_ttm", res["f164"])

        item_loader2.add_value("gpm", float(res["f49"]) * 100)
        item_loader2.add_value("npmos", float(res["f129"]) * 100)
        item_loader2.add_value("roe", float(res["f37"]) * 100)
        item_loader2.add_value("type", 'gpm')
        yield item_loader2.load_item()

        # 行业 1
        # f2009 市盈率(动)
        # f12 股票代码
        # f2023 市净率
        # f2037 ROE
        # f2049 毛利率
        # f2129 净利率
        res = result["data"]["diff"][1]
        item_loader3 = ItemLoader(item=SharesInfoItems.Items())
        item_loader3.add_value("code", res["f12"])
        item_loader3.add_value("pb", float(res["f2023"]) * 100)
        # item_loader2.add_value("pe", res["f9"])
        item_loader3.add_value("pe_d", float(res["f2009"]) * 100)
        # item_loader2.add_value("pe_ttm", res["f164"])

        item_loader3.add_value("gpm", float(res["f2049"]) * 100)
        item_loader3.add_value("npmos", float(res["f2129"]) * 100)
        item_loader3.add_value("roe", float(res["f2037"]) * 100)
        item_loader3.add_value("type", 'gpm')

        s = item_loader3.load_item()
        if int(s['gpm'][0]) == 0 and int(s['npmos'][0]) == 0 and int(s['pb'][0]) == 0 and int(s['pe_d'][0]) == 0 and int(s['roe'][0]):
            print(res["f12"], item_loader3.load_item())
            return
        yield item_loader3.load_item()

        pass

    def parse_content2(self, response):
        result = json.loads(response.text)
        if "data" not in result:
            return
        if result["data"] is None or "diff" not in result["data"]:
            return
        res = result["data"]["diff"][0]
        item_loader2 = ItemLoader(item=SharesInfoItems.Items())
        item_loader2.add_value("code", res["f57"])
        item_loader2.add_value("pe", float(res["f163"]) * 100)
        item_loader2.add_value("pe_ttm", float(res["f164"])  * 100)
        item_loader2.add_value("type", 'pe_ttm')
        yield item_loader2.load_item()
        pass

    def findStoks(self):
        sql = 'select mc_shares_name.code,mc_shares_name.name,mc_shares_name.area_id, industry_code_id ' \
              'from mc_shares_name ' \
              'left join mc_shares_join_industry on mc_shares_name.code = mc_shares_join_industry.code_id ' \
              'where status = 1 and code_type =1';
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
