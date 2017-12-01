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
            items = response.css(".j-r-list-c .j-video-c>div:first-child::attr(data-mp4)").extract()
            itemsThumbnail = response.css(".j-r-list-c .j-video-c>div:first-child::attr(data-poster)").extract()
            itemTitles = response.css(".j-r-list-c .j-r-list-c-desc a").extract()
            type = 1
        elif type == '图片':
            itemList = response.css(".j-r-list li");
            type = 2;
            for item in itemList:
                thumbnail = item.css(".j-r-list-c img::attr(data-original)").extract_first();
                desc = item.css(".j-r-list-c .j-r-list-c-desc a::text").extract_first();
                title = item.css(".j-r-list-tool::attr(data-title)").extract_first();
                if desc:
                    desc = '<p>' + desc + '</p>'
                if thumbnail:
                    src = '<p><img src=' + thumbnail  + ' /></p>'
                    yield self.parse_content({
                        'body': '<div class="content">' + desc + src + '</div>',
                        'src': thumbnail,
                        'type': type,
                        'thumbnail': thumbnail,
                        'title': title,
                    });


        elif type == '段子':
            items = response.css(".j-r-list-c a").extract()
            itemsThumbnail = itemTitles = response.css(".j-r-list-tool::attr(data-title)").extract()
            type = 3

        for key, item in enumerate(items):
            yield self.parse_content({
                'body': item,
                'src': item,
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
        item_loader.add_value("src", article.get("src", 0))
        # 文档标题
        item_loader.add_value("title", article.get("title", 0))
        item_loader.add_value("title", article.get("title", 0))
        # content
        item_loader.add_value("body", article.get("body", ''))
        # 文档URL
        item_loader.add_value("type", article.get("type", ''))
        return item_loader.load_item()


