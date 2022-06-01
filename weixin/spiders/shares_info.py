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
    allowed_domains = [ '.10jqka.com.cn']
    # allowed_domains = ['.eastmoney.com', '.10jqka.com.cn']
    start_urls = []
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
        # for item in results:
        #     code = item[0]
        #     area_id = item[2]
        #     if area_id == 1:
        #         s_code = "1." + code
        #     else:
        #         s_code = "0." + code
        #     url = self.get_url(s_code)
        #     yield scrapy.Request(url,
        #                          headers=self.headers,
        #                          dont_filter=True,
        #                          callback=self.parse_content)
        #     break

        for item in results:
            yield self.request_info(item)
            # yield time.sleep(5)
            break

    def request_info(self, item):
        code = item[0]
        industry_code = item[3]
        headers = copy.deepcopy(self.headers)
        headers['HOST'] = "doctor.10jqka.com.cn"
        headers['code'] = code
        headers['industry_code'] = industry_code
        url = "http://doctor.10jqka.com.cn/" + str(code) + "/#nav_basic"
        print(url)
        return scrapy.Request(url,
                              headers=headers,
                              dont_filter=True,
                              callback=self.parse_content_info)

    def parse_content_info(self, response):
        code = response.request.headers.getlist('code')[0].decode("UTF-8")
        industry_code = response.request.headers.getlist('industry_code')[0].decode("UTF-8")

        yysrzzl = response.css("#yysrzzl  tr")
        jlrzzl = response.css("#jlrzzl  tr")
        print(yysrzzl, jlrzzl)
        gpm_ex = yysrzzl[1].css("td")[1].get()
        npmos_ex = jlrzzl[1].css("td")[1].get()
        item_loader2 = ItemLoader(item=SharesInfoItems.Items())
        item_loader2.add_value("code", code)
        item_loader2.add_value("gpm_ex", gpm_ex * 100)
        item_loader2.add_value("npmos_ex", npmos_ex * 100)
        print(item_loader2.load_item())
        yield item_loader2.load_item()

        gpm_ex = yysrzzl[2].css("td")[1].get()
        npmos_ex = jlrzzl[2].css("td")[1].get()
        item_loader3 = ItemLoader(item=SharesInfoItems.Items())
        item_loader3.add_value("code", industry_code)
        item_loader3.add_value("gpm_ex", gpm_ex * 100)
        item_loader3.add_value("npmos_ex", npmos_ex * 100)
        print(item_loader3.load_item())
        yield item_loader3.load_item()

        pass

    def parse_content(self, response):
        result = json.loads(response.text)
        if "data" not in result:
            return
        if "diff" not in result["data"]:
            return

        res = result["data"]["diff"][0]
        item_loader2 = ItemLoader(item=SharesInfoItems.Items())
        item_loader2.add_value("code", res["f12"])
        item_loader2.add_value("pb", res["f23"] * 100)
        # item_loader2.add_value("pe", res["f9"])
        item_loader2.add_value("pe_d", res["f9"] * 100)
        # item_loader2.add_value("pe_ttm", res["f164"])

        item_loader2.add_value("gpm", res["f49"] * 100)
        item_loader2.add_value("npmos", res["f129"] * 100)
        item_loader2.add_value("roe", res["f37"] * 100)
        yield item_loader2.load_item()

        # 行业 1
        # f9 市盈率(动)
        # f12 股票代码
        # f23 市净率
        # f37 ROE
        # f49 毛利率
        # f129 净利率
        res = result["data"]["diff"][1]
        item_loader3 = ItemLoader(item=SharesInfoItems.Items())
        item_loader3.add_value("code", res["f12"])
        item_loader3.add_value("pb", res["f23"] * 100)
        # item_loader2.add_value("pe", res["f9"])
        item_loader3.add_value("pe_d", res["f9"] * 100)
        # item_loader2.add_value("pe_ttm", res["f164"])

        item_loader3.add_value("gpm", res["f49"] * 100)
        item_loader3.add_value("npmos", res["f129"] * 100)
        item_loader3.add_value("roe", res["f37"] * 100)
        yield item_loader3.load_item()

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
