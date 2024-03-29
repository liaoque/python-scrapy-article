import scrapy
import json

from scrapy.loader import ItemLoader
import weixin.shares.items as SharesItems
import weixin.shares.items_industry as SharesItemsIndustry
import weixin.shares.items_block as SharesItemsBlock
import time
import copy

# https://zx.10jqka.com.cn/indval/getstocks?blockcode=881102
# https://ai.10jqka.com.cn/transfer/industry/getpickstock
# https://zx.10jqka.com.cn/indval/getallindustry


# http://zx.10jqka.com.cn/indval/getallindustry
# https://www.liujiangblog.com/course/django/88
class Shares_industry(scrapy.Spider):
    name = 'shares_industry'
    total = 1
    allowed_domains = ['.eastmoney.com']
    start_urls = []
    area_map = {
        "SH": "m:1+t:2,m:1+t:23",
        "SZ": "m:0+t:6,m:0+t:80",
        "BJ": "m:0+t:81+s:2048",
    }
    headers = {
        "HOST": "92.push2.eastmoney.com"
    }

    def get_url(self, industry):
        return "http://92.push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=1000&po=1&" \
               "np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=b:" + \
               str(industry) + "+f:!50&fields=f12,f14&_=1641007887744"


    # http://11.push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152&_=1584074266443"
    def start_requests(self):
        url = "https://56.push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=1000&" \
              "po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&" \
              "fs=m:90+t:2+f:!50&fields=f12,f13,f14&_=1641007970988"
        yield scrapy.Request(url, callback=self.parse_each, dont_filter=True)

        url = "https://35.push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=1000&po=1&np=1" \
              "&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&wbp2u=5204545223982760|0|1|0|web" \
              "&fid=f3&fs=m:90+t:3+f:!50&fields=f12,f13,f14&_=1653722690074"
        yield scrapy.Request(url, callback=self.parse_each_block, dont_filter=True)


    def parse_each(self, response):
        result = json.loads(response.text)
        # total = int(result["data"]["total"])
        for item in result["data"]["diff"]:
            url = self.get_url(item["f12"])
            headers = copy.deepcopy(self.headers)
            headers['industry_code'] = item["f12"]
            headers['industry_type'] = item["f13"]
            headers['industry_name'] = item["f14"]
            yield scrapy.Request(url, headers=headers, callback=self.parse_content, dont_filter=True)

# "https://46.push2.eastmoney.com/api/qt/clist/get?cb=&pn=2&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=b:BK0484+f:!50&fields=f1&_=1641013357526"
# "http://92.push2.eastmoney.com/api/qt/clist/get?cb=&pn=2&pz=1000&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=b:BK0484+f:!50&fields=f12,f14&_=1641007887744"
    def parse_content(self, response):
        industry_code = response.request.headers.getlist('industry_code')[0].decode("UTF-8")
        industry_name = response.request.headers.getlist('industry_name')[0].decode("UTF-8")
        print("加入行业：%s" % (industry_name))
        item_loader = ItemLoader(item=SharesItems.Items())
        item_loader.add_value("code", industry_code)
        item_loader.add_value("name", industry_name)
        item_loader.add_value("area_id", '90')
        item_loader.add_value("status", '1')
        item_loader.add_value("code_type", '2')
        item_loader.add_value("pe", '0')
        item_loader.add_value("pb", '0')
        yield item_loader.load_item()

        result = json.loads(response.text)
        for item in result["data"]["diff"]:
            name = item["f14"] + ""
            code_id = item["f12"] + ""
            if code_id < '100000' or (code_id < '400000' and code_id >= '300000') or  (code_id < '700000' and code_id >= '600000') :
                print("加入行业：%s--%s" % (industry_name, name))
                item_loader2 = ItemLoader(item=SharesItemsIndustry.Items())
                item_loader2.add_value("code_id", code_id)
                item_loader2.add_value("industry_code_id", industry_code)
                yield item_loader2.load_item()

    def parse_each_block(self, response):
        result = json.loads(response.text)
        # total = int(result["data"]["total"])
        for item in result["data"]["diff"]:
            url = self.get_url(item["f12"])
            headers = copy.deepcopy(self.headers)
            headers['block_code'] = item["f12"]
            headers['block_type'] = item["f13"]
            headers['block_name'] = item["f14"]
            yield scrapy.Request(url, headers=headers, callback=self.parse_content_block, dont_filter=True)


    def parse_content_block(self, response):
        block_code = response.request.headers.getlist('block_code')[0].decode("UTF-8")
        block_name = response.request.headers.getlist('block_name')[0].decode("UTF-8")
        print("加入板块：%s" % (block_name))
        item_loader = ItemLoader(item=SharesItems.Items())
        item_loader.add_value("code", block_code)
        item_loader.add_value("name", block_name)
        item_loader.add_value("area_id", '90')
        item_loader.add_value("status", '1')
        item_loader.add_value("code_type", '3')
        item_loader.add_value("pe", '0')
        item_loader.add_value("pb", '0')
        yield item_loader.load_item()

        result = json.loads(response.text)
        for item in result["data"]["diff"]:
            name = item["f14"] + ""
            code_id = item["f12"] + ""
            if code_id < '100000' or (code_id < '400000' and code_id >= '300000') or  (code_id < '700000' and code_id >= '600000') :
                print("加入板块：%s--%s" % (block_name, name))
                item_loader2 = ItemLoader(item=SharesItemsBlock.Items())
                item_loader2.add_value("code_id", code_id)
                item_loader2.add_value("block_code_id", block_code)
                item_loader2.add_value("code_type", 1)
                yield item_loader2.load_item()
