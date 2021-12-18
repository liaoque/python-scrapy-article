import scrapy
import json
from scrapy.loader import ItemLoader
import sys
import re

import weixin.shares.items as SharesItems
import time


class Shares_name(scrapy.Spider):
    name = 'shares_name'
    total = 1
    allowed_domains = ['.eastmoney.com']
    start_urls = []
    area_map = {
        "SH": "m:0+t:6,m:0+t:80",
        "SZ": "m:0+t:6,m:0+t:80",
        "BJ": "m:0+t:6,m:0+t:80",
    }
    headers = {
        "HOST": "push2.eastmoney.com"
    }

    def get_url(self, n, area):
        return "https://75.push2.eastmoney.com/api/qt/clist/get?cb=&pn=" + str(n) + "&pz=200&po=1&np=1&" \
                                                                                    "ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f12&fs=" + area + "&fields=f12,f13,f14&_=1639813284425"

    # http://11.push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152&_=1584074266443"
    def start_requests(self):
        self.total = n = 1

        self.headers['area'] = "SZ"
        url = self.get_url(1, self.area_map["SZ"])
        yield scrapy.Request(url, headers=self.headers, callback=self.parse_each)

        url = self.get_url(1, self.area_map["SH"])
        yield scrapy.Request(url, headers=self.headers, callback=self.parse_each)

        url = self.get_url(1, self.area_map["BJ"])
        yield scrapy.Request(url, headers=self.headers, callback=self.parse_each)

    def parse_each(self, response):
        result = json.loads(response.text)
        total = result["data"]["total"] / 200 + 1
        area = response.request.headers.getlist('area')[0].decode("UTF-8")
        self.headers['area'] = area
        area = self.area_map[area]
        n = 1
        while n <= self.total:
            url = self.get_url(n, area)
            yield scrapy.Request(url, headers=self.headers, callback=self.parse_each)

    def parse_content(self, response):
        result = json.loads(response.text)
        self.total = result["data"]["total"] / 200 + 1
        area = response.request.headers.getlist('area')[0].decode("UTF-8")
        for item in result["data"]["diff"]:
            name = item["f14"] + ""
            code = item["f12"] + ""
            print(name, code)
            item_loader = ItemLoader(item=SharesItems.Items())
            item_loader.add_value("code", code)
            item_loader.add_value("name", name)
            item_loader.add_value("area_id", area)
            pass
