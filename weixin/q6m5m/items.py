# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from weixin.utils.common import md5
from weixin.utils.htmlfilter import filter_tags


class Items(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    md5url = scrapy.Field()
    img = scrapy.Field()
    text_type = scrapy.Field()


    def save(self, cursor):
        md5url = md5(self['url'][0])
        textType = re.sub('素材分类：\s+', '', self["text_type"][0])
        sql = "SELECT id FROM mc_6m5m  WHERE md5url = '%s' " % (md5url)
        cursor.execute(sql);
        if cursor.rowcount:
            return
        sql = """
            INSERT INTO mc_6m5m (url, md5url, title, img, text_type)
            VALUES (%s, %s, %s,  %s,  %s)
            """;
        params = (
            self["url"][0],
            md5url,
            self["title"][0],
            self["img"][0],
            textType
        )
        cursor.execute(sql, params)
        pass
    pass