# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.loader import ItemLoader
import sys

import weixin.bsbudejie.items as BaiSiBuDeJieItem
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
            srcs = items = response.css(".j-r-list-c .j-video-c>div:first-child::attr(data-mp4)").extract()
            itemsThumbnail = response.css(".j-r-list-c .j-video-c>div:first-child::attr(data-poster)").extract()
            itemTitles = response.css(".j-r-list-c .j-r-list-c-desc a").extract()
            type = 1
        elif type == '图片':
            srcs = items = response.css(".j-r-list-c img::attr(data-original)").extract()
            itemsThumbnail = itemTitles = response.css(".j-r-list-tool::attr(data-title)").extract()
            type = 2
        elif type == '段子':
            srcs = items = response.css(".j-r-list-c a").extract()
            itemsThumbnail = itemTitles = response.css(".j-r-list-tool::attr(data-title)").extract()
            type = 3

        for key, item in items:
            yield self.parse_content({
                'body': item,
                'type': type,
                'thumbnail': itemsThumbnail[key],
                'title': itemTitles[key],
            })

        pass

    def parse_content(self, item):
        article = item;
        item_loader = ItemLoader(item=BaiSiBuDeJieItem.Items())
        # 缩略图
        item_loader.add_value("thumbnail", article.get("thumbnail", 0))
        # 文档标题
        item_loader.add_value("title", article.get("Title", 0))
        # content
        item_loader.add_value("body", article.get("body", ''))
        # 文档URL
        item_loader.add_value("type", article.get("type", ''))
        return item_loader.load_item()


