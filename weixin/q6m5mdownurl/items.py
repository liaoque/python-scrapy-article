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
    md5url = scrapy.Field()
    zip_url = scrapy.Field()


    def save(self, cursor):
        md5url = md5(self['url'][0])
        zip_url = self['zip_url'][0]

        sql = "update mc_6m5m set zip_url = '%s',status = 200  WHERE md5url = '%s' " % (zip_url, md5url)
        cursor.execute(sql);
        if cursor.rowcount:
            return
        sql = """
            INSERT INTO mc_6m5m (url, md5url, zip_url)
            VALUES (%s, %s, %s)
            """;
        params = (
            self["url"][0],
            md5url,
            zip_url
        )
        cursor.execute(sql, params)
        pass
    pass

