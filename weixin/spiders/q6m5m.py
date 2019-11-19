

import scrapy
import json
from scrapy.loader import ItemLoader
import sys


import weixin.q6m5m.items as Q6m5mItems
import time

class Q6m5m(scrapy.Spider):
    name = 'q6m5m'
    allowed_domains = ['.6m5m.com']
    start_urls = [ ]

    headers = {
        "HOST": "6m5m.com"
    }

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        n = 1
        while n < 1321:
            url = 'http://www.6m5m.com/shop_list-page-' + str(n) + '.html';
            self.start_urls.append(url)
            n = n+1
        pass



    def parse(self, response):
        result = response.css(".grid_25 #container .box")
        for res in result:
            yield self.parse_content(res) 
    pass

    
    def parse_content(self, response):
        title = response.css('span a::text').extract_first();
        url = response.css('span a::attr(href)').extract_first();
        img = response.css('img::attr(src)').extract_first();
        text_type = response.css('.h70 .fl_l::text').extract_first();


        item_loader = ItemLoader(item=Q6m5mItems.Items())

        # 文档标题
        item_loader.add_value("title", title)
        item_loader.add_value("img", img)
        item_loader.add_value("url", url)
        item_loader.add_value("text_type", text_type)
        return item_loader.load_item()
    pass