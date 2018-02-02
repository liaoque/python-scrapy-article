# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.loader import ItemLoader
import sys

import weixin.qsbaike.items as QiuShiBaiKeItem
from weixin.utils.common import md5
import time
import re

from scrapy.selector import Selector


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
            idLits = response.css("#newsList .item a::attr(data-id)").extract()
            thumbnailList = response.css("#newsList .item a img::attr(data-src)").extract()
            for key, item in enumerate(result):
                url = self.base_url + item
                meta = {
                    'id': idLits[key],
                    'thumbnail': thumbnailList[key]
                }
                # url = 'https://www.qiushibaike.com/news/article-79021.html';
                yield scrapy.Request(url,
                                     meta = meta,
                                     dont_filter=True,
                                     callback=self.parse_content)
        elif index == 1:
            result = response.css("main .pic-wrapper a::attr(href)").extract()
            idLits = response.css("main .pic-wrapper::attr(data-id)").extract()
            for key, item in enumerate(result):
                url = self.base_url + item;
                meta = {
                    'id': idLits[key]
                }
                yield scrapy.Request(url,
                                     meta=meta,
                                     dont_filter=True,
                                     callback=self.parse_images)
        pass

    def parse_content(self, response):
        title = response.css('article h1::text').extract_first("")
        content = ''
        result= response.css('script::text').extract()
        for item in result:
            item = item.replace('\n', '')
            pattern = re.compile('var\s*content\s*=\s*\'')
            if pattern.match(item):
                body = '<div class="xsa">' + pattern.sub('', item) + '</div>'
                body = Selector(text=body)
                pTags = body.css('div.xsa p')
                for pTag in pTags:
                    # imageList = pTag.css('img::attr(data-src)').extract()
                    imageList = pTag.xpath('img').xpath('@data-src').extract()
                    text = pTag.css('::text').extract()
                    html = ''
                    if imageList:
                        html = ''.join(['<p><img src="' + image + '"/></p>' for image in imageList])
                    elif text:
                        html = '<p>' + ''.join(text) + '</p>'
                    content += html
                if content:
                    yield QiuShiBaiKeItem.Items({
                        'id': int(response.meta['id']),
                        'title': title,
                        'thumbnail': response.meta['thumbnail'],
                        'body': content,
                        'view_url': response.url,
                        'type': 1
                    })


            # if item.find('var content') == 0:
            #     item = re.sub(r'var\s*content\s*=\s*', '', item)
                # content = re.search(r"[^']+", item, re.M)
        pass

    # 美女图片
    def parse_images(self, response):
        title = response.css('.info-wrapper h2.title::text').extract_first("")
        imageList = response.css('.pic-wrapper img.carousel-cell-image::attr(data-flickity-lazyload)').extract()
        yield QiuShiBaiKeItem.Items({
            'id': int(response.meta['id']),
            'title': title,
            'thumbnail': imageList[0],
            'body': imageList,
            'view_url': response.url,
            'type': 2
        })

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

