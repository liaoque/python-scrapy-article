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

class XiaoShenLaiLe(scrapy.Spider):
    name = 'xiaoshenlaile'
    allowed_domains = ['.xiaobaxiaoba.com/']
    start_urls = [
        {
            'categoryId': 16,
            'url': 'http://xiaobaxiaoba.com/?json=gender/category_article_list_new_v2',
        }, {
            'categoryId': 1,
            'url': 'http://xiaobaxiaoba.com/?json=gender/category_article_list_new_v2',
        }, {
            'categoryId': 29,
            'url': 'http://xiaobaxiaoba.com/?json=gender/category_article_list_new_v2',
        }
    ]
    base_url = 'http://www.xiaobaxiaoba.com/web/statics/js/manage_cookie.js';

    headers = {
        "HOST": "xiaobaxiaoba.com",
        "Content-Type": "application/x-www-form-urlencoded",
        'User-Agent': "Android/4.4.2/2.1.37_0923_yybao/864394010252171/b4dd214d26c744bba9f271c1ac8cfaf7/FC:AA:14:99:2E:B6/FCAA14992EB60000"
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
        item_loader = ItemLoader(item=XiaoShenLaiLeItems.Items())
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
        for item in self.start_urls:
            body = {
                'timestamp': time.time(),
                'afterDate': 0,
                'v': '2137',
                'categoryId': item['categoryId'],
            }
            data = [(k.lower() + str(body[k])) for k in sorted(body.keys())];
            body['sign'] = md5(''.join(data)).upper()
            body='&'.join([(k + '=' + str(body[k])) for k in body.keys()])
            yield scrapy.Request(item['url'],
                                 method='POST',
                                 body=body,
                                 headers=self.headers,
                                 dont_filter=True)