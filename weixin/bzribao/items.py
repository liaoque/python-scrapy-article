# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy



class Items(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    thumbnail = scrapy.Field()
    title = scrapy.Field()
    key_words = scrapy.Field()
    body = scrapy.Field()
    article_type = scrapy.Field()
    view_url = scrapy.Field()

    author_name = scrapy.Field()
    author_face = scrapy.Field()

    cur_url = scrapy.Field()
    fingerprint = scrapy.Field()


    def get_insert_sql(self):
        return ''


    pass

