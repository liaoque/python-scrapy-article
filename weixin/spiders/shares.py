

import scrapy
import json
from scrapy.loader import ItemLoader
import sys


import weixin.shares.items as SharesItems
import time

class Shares(scrapy.Spider):
    name = 'shares'
    allowed_domains = ['.eastmoney.com']
    start_urls = [ ]
    headers = {
        "HOST": "push2.eastmoney.com"
    }

# http://11.push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152&_=1584074266443"
    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        n = 1
        while n <= 226:
            url = 'http://11.push2.eastmoney.com/api/qt/clist/get?cb=&pn=' + str(n) \
                  + '&pz=20&po=0&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f12&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23' \
                    '&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152' \
                    '&_=' + str(time.time())
            # url = 'http://www.6m5m.com/shop_list-page-' + str(n) + '.html';
            # print(url)
            self.start_urls.append(url)
            n = n+1
        pass



    def parse(self, response):
        result = json.loads(response.text)
        end = time.strftime("%Y%m%d", time.localtime())
        for item in result["data"]["diff"]:
        #    print(end)
            # https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.688037&cb=fsdata1584074280&klt=101&fqt=0&lmt=10&end=20200313&iscca=1&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58"
            url = 'https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=' + str(item["f13"]) + '.' + str(item["f12"]) + '&cb=&klt=101&fqt=0&lmt=300&end=' + str(end) + '&iscca=1&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58'
            yield scrapy.Request(url,
                            headers=self.headers,
                            dont_filter=True,
                            callback=self.parse_content)
        pass

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
            item_loader = ItemLoader(item=SharesItems.Items())

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
        
        # return item_loader.load_item()
    pass