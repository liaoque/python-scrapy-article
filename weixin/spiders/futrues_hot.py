import scrapy
import json

from scrapy.loader import ItemLoader
import weixin.shares.items as SharesItems
import time
import copy


#
# 热门金属列表
# http://ai.10jqka.com.cn/commodity/stocklinkage/info/getdetail
#
# 热门商品咨询
# http://ai.10jqka.com.cn/commodity/stocklinkage/info/getconsultation?indexid=S002981544
#
# 历史价格
# http://ai.10jqka.com.cn/commodity/stocklinkage/info/commodityhistory?indexid=S004242721&daynum=60
#
# 关联股票
# http://ai.10jqka.com.cn/commodity/stocklinkage/info/stocklink?commodityid=301
class futrues_hot(scrapy.Spider):
    name = 'futrues_hot'
    total = 1
    allowed_domains = ['.10jqka.com.cn']
    start_urls = []

    headers = {
        "HOST": "ai.10jqka.com.cn"
    }

    def get_url(self, n, area):
        return "http://ai.10jqka.com.cn/commodity/stocklinkage/info/stocklink?commodityid=" + str(n)

    def start_requests(self):
        url = "http://ai.10jqka.com.cn/commodity/stocklinkage/info/getdetail"
        headers = self.headers
        return scrapy.Request(url, headers=headers, callback=self.parse_each, dont_filter=True)

    def parse_each(self, response):
        result = json.loads(response.text)
        result = result["result"]
        for item in result:
            url = self.get_url(item['id'])
            headers = self.headers
            headers['id'] = item['id']
            headers['code'] = item['index_id']
            headers['name'] = item['name']
            headers['industry'] = item['first_industry']
            headers['today_zdf'] = item['zdf']
            headers['five_zdf'] = item['five_days_zdf']
            headers['ten_zdf'] = item['ten_days_zdf']
            headers['twenty_zdf'] = item['twenty_days_zdf']
            headers['sixty_zdf'] = item['sixty_days_zdf']
            yield scrapy.Request(url, headers=headers, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        result = json.loads(response.text)
        result = result["result"]
        for item in result:
            item_loader = ItemLoader(item=SharesItems.Items())
            item_loader.add_value("id", response.request.headers.getlist("id")[0].decode("UTF-8"))
            item_loader.add_value("code", response.request.headers.getlist("code")[0].decode("UTF-8"))
            item_loader.add_value("stock_code", item["stock_code"])
            item_loader.add_value("name", response.request.headers.getlist("name")[0].decode("UTF-8"))
            item_loader.add_value("industry", response.request.headers.getlist("industry")[0].decode("UTF-8"))
            item_loader.add_value("today_zdf", response.request.headers.getlist("today_zdf")[0].decode("UTF-8"))
            item_loader.add_value("five_zdf", response.request.headers.getlist("five_zdf")[0].decode("UTF-8"))
            item_loader.add_value("ten_zdf", response.request.headers.getlist("ten_zdf")[0].decode("UTF-8"))
            item_loader.add_value("twenty_zdf", response.request.headers.getlist("twenty_zdf")[0].decode("UTF-8"))
            item_loader.add_value("sixty_zdf", response.request.headers.getlist("sixty_zdf")[0].decode("UTF-8"))
            yield item_loader.load_item()
