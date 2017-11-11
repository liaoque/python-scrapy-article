# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.loader import ItemLoader
import sys

import weixin.xslaile.items as XiaoShenLaiLeItems
from weixin.utils.common import md5
import time


# import baozouribao.items

# from scrapy.spiders import CrawlSpider, Rule
# from scrapy.linkextractors import LinkExtractor

class BaiSiBuDeJie(scrapy.Spider):
    name = 'baisibudejie'
    allowed_domains = ['.budejie.com']
    start_urls = [
        'http://www.budejie.com/text/',
        'http://www.budejie.com/video/',
        'http://www.budejie.com/pic/',
    ]

    headers = {
        "HOST": "budejie.com"
    }

    # custom_settings = {
    #     "COOKIES_ENABLED": True
    # }

    def parse(self, response):
        type = response.css(".j-top a.cur::text").extract_first("")
        items = []
        if type == '视频':
            items = response.css(".j-r-list-c .j-video-c>div:first-child::attr(data-mp4)").extract()
            itemTitles = response.css(".j-r-list-c .j-video-c::attr(data-title)").extract()
            type = 1
        elif type == '图片':
            items = response.css(".j-r-list-c img::attr(data-original)").extract()
            itemTitles = response.css(".j-r-list-tool::attr(data-title)").extract()
            type = 2
        elif type == '段子':
            items = response.css(".j-r-list-c a::text").extract()
            itemTitles = response.css(".j-r-list-tool::attr(data-title)").extract()
            type = 3

        for key, item in items:
            print({
                'title':itemTitles[key],
                'body':item,
                'type': type
            })
        pass

    def parse_content(self, item):


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

