# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.loader import ItemLoader
import sys


import weixin.bzribao.items as baozouribaoItems
from weixin.utils.common import md5

# import baozouribao.items

# from scrapy.spiders import CrawlSpider, Rule
# from scrapy.linkextractors import LinkExtractor

class BaozouribaoSpider(scrapy.Spider):
    name = 'baozouribao'
    allowed_domains = ['baozouribao.com']
    start_urls = ['http://baozouribao.com/documents']
    base_url = 'http://baozouribao.com/';

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "HOST": "baozouribao.com",
        "Referer": "http://baozouribao.com",
        "X-Requested-With": "XMLHttpRequest",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }

    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def parse(self, response):
        result = json.loads(response.text)
        for item in result["documents"]:
            yield scrapy.Request(item["url"],
                                 headers=self.headers,
                                 dont_filter=True,
                                 callback=self.parse_content)
        pass

    def parse_content(self, response):
        print(response)
        item_loader = ItemLoader(item=baozouribaoItems.Items(), response=response)
        item = json.loads(response.text)
        # 文档id
        item_loader.add_value("id", item.get("document_id", 0))
        # 缩略图
        item_loader.add_value("thumbnail", item.get("thumbnail", ''))
        # 标题
        item_loader.add_value("title", item.get("title", ''))
        # 关键字
        item_loader.add_value("key_words", item.get("key_words", ''))
        # 内容
        item_loader.add_value("body", item.get("body", ''))
        # 文章类型
        item_loader.add_value("article_type", item.get("article_type", 1))
        # 文档URL
        item_loader.add_value("view_url", item.get("view_url", ''))
        # 作者头像
        item_loader.add_value("author_face", item.get("author_face", ''))
        # 作者名字
        item_loader.add_value("author_name", item.get("author_name", ''))
        # api接口
        item_loader.add_value("cur_url", response.url)
        # 指纹
        item_loader.add_value("fingerprint", md5(response.url))
        # 延迟时间
        # item_loader.add_value("display_time", item.display_time)
        # 点击数
        # item_loader.add_value("hit_count", item.hit_count)
        # 点击数字体颜色
        # item_loader.add_value("hit_count_string", item.hit_count_string)
        # 颜色
        # item_loader.add_value("section_color", item.section_color)
        #
        # item_loader.add_value("section_id", item.section_id)
        #
        # item_loader.add_value("section_image", item.section_image)
        #
        # item_loader.add_value("section_name", item.section_name)
        yield item_loader.load_item()
        pass

    def start_requests(self):
        # return [scrapy.FormRequest(
        #     url='http://baozouribao.com/',
        #     formdata={
        #     },
        #     headers=self.headers,
        #     callback=self.get_csrf_token,
        #     method='GET'
        # )]
        return [scrapy.Request(self.base_url, callback=self.get_csrf_token)]

    def get_csrf_token(self, response):
        xsrf = response.css("meta[name='csrf-token']::attr(content)").extract_first("")
        if xsrf:
            self.headers['X-CSRF-Token'] = xsrf
            for url in self.start_urls:
                yield scrapy.Request(url, headers=self.headers)
