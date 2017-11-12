# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.loader import ItemLoader
import sys

import weixin.xslaile.items as XiaoShenLaiLeItems
from weixin.utils.common import md5
import time
import re

# import baozouribao.items

# from scrapy.spiders import CrawlSpider, Rule
# from scrapy.linkextractors import LinkExtractor

class QiuShiBaiKe(scrapy.Spider):
    name = 'qiushibaike'
    allowed_domains = ['.budejie.com']
    start_urls = [
        'https://www.qiushibaike.com/news/',
        'https://www.qiushibaike.com/img/0.html'
    ]

    base_url = 'https://www.qiushibaike.com'

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "HOST": "budejie.com"
    }

    # custom_settings = {
    #     "COOKIES_ENABLED": True
    # }

    def parse(self, response):

        index = self.start_urls.index(response.request.url)
        if index == 0:
            result = response.css("#newsList .item a::attr(href)").extract()
            for item in result:
                url = self.base_url + item;
                yield scrapy.Request(url,
                                     dont_filter=True,
                                     callback=self.parse_content)
        elif index == 1:
            result = response.css("main .pic-wrapper a::attr(href)").extract()
            for item in result:
                url = self.base_url + item;
                yield scrapy.Request(url,
                                     dont_filter=True,
                                     callback=self.parse_images)


        pass

    def parse_content(self, response):
        title = response.css('article h1::text').extract_first("")
        content = ''
        result= response.css('script::text').extract()
        for item in result:
            item= item.replace('\n', '')
            if item.find('var content') == 0:
                item = re.sub(r'var\s*content\s*=\s*', '', item)
                content = re.search(r"[^']+", item, re.M)
        pass

    # 美女图片
    def parse_images(self, response):
        title = response.css('.info-wrapper h2.title::text').extract_first("")
        images = response.css('.pic-wrapper img.carousel-cell-image::attr(data-flickity-lazyload)').extract()
        # article = item;
        # item_loader = ItemLoader(item=XiaoShenLaiLeItems.Items())
        # # 文档id
        # item_loader.add_value("id", article.get("ArticleId", 0))
        # # 文档标题
        # item_loader.add_value("title", article.get("Title", 0))
        # # content
        # item_loader.add_value("body", article.get("Content", ''))
        # # 图片
        # item_loader.add_value("pic", article.get("Pic", ''))
        # # 文档URL
        # item_loader.add_value("type", article.get("CategoryId", ''))
        # # 指纹
        # item_loader.add_value("fingerprint", md5(article.get("share_url", '')))
        # yield item_loader.load_item()
        pass

