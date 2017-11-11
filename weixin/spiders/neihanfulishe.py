# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.loader import ItemLoader
import sys


import weixin.nhduanzi.items as NeiHanDuanZiItems
from weixin.utils.common import md5

# import baozouribao.items

# from scrapy.spiders import CrawlSpider, Rule
# from scrapy.linkextractors import LinkExtractor

class NeiHanFuLiShe(scrapy.Spider):
    name = 'neihanfulishe'
    allowed_domains = ['.neihanshequ.com/']
    start_urls = ['http://m.neihanshequ.com/']
    base_url = 'http://m.neihanshequ.com/';

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "HOST": "m.neihanshequ.com",
        "Referer": "http://m.neihanshequ.com",
        "X-Requested-With": "XMLHttpRequest",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }

    # custom_settings = {
    #     "COOKIES_ENABLED": True
    # }

    def parse(self, response):
        result = json.loads(response.text)
        for item in result["data"]["data"]:
            self.parse_content(item)
        pass

    def parse_content(self, item):
        article = item.get("group");
        item_loader = ItemLoader(item=NeiHanDuanZiItems.Items())
        # 文档id
        item_loader.add_value("id", article.get("id", 0))
        # content
        item_loader.add_value("body", article.get("content", ''))
        # 文档URL
        item_loader.add_value("view_url", article.get("share_url", ''))
        # 指纹
        item_loader.add_value("fingerprint", md5(article.get("share_url", '')))
        yield item_loader.load_item()
        pass

    def start_requests(self):
        return [scrapy.Request(self.base_url, callback=self.get_csrf_token)]

    def get_csrf_token(self, response):

        xsrf = response.css("input[name='csrfmiddlewaretoken']::attr(value)").extract_first("")
        if xsrf:
            coo = response.headers.getlist('Set-Cookie')
            # self.headers['X-CSRF-Token'] = xsrf
            for url in self.start_urls:
                # http: // m.neihanshequ.com /?is_json = 1 & app_name = neihanshequ_web & min_time = & csrfmiddlewaretoken = 5c830f21c8ad59a3a2803ccab1fe7749
                url = url + '?is_json=1&app_name=neihanshequ_web&min_time=&csrfmiddlewaretoken='+xsrf+'&skip_guidence=1';
                yield scrapy.Request(url, cookies=coo, headers=self.headers, dont_filter=True)
