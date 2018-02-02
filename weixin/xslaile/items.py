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
    # thumbnail = scrapy.Field()
    title = scrapy.Field()
    # key_words = scrapy.Field()
    body = scrapy.Field()
    pic = scrapy.Field()
    type = scrapy.Field()
    view_url = scrapy.Field()

    # author_name = scrapy.Field()
    # author_face = scrapy.Field()

    # cur_url = scrapy.Field()
    fingerprint = scrapy.Field()


    def save(self, cursor):
        body = self["body"][0]
        fingerprint = self["fingerprint"][0]
        sql = "SELECT id FROM mc_duanzi  WHERE fingerprint = '%s' " % (fingerprint)
        cursor.execute(sql)
        if cursor.rowcount:
            return
        if self["body"] > 45:
            status = 1
        else:
            status = 2
        sql = """
                    INSERT INTO mc_duanzi (body, fingerprint, status)
                    VALUES (%s, %s, %s)
                    """;
        params = (
            body,
            fingerprint,
            status
        )
        cursor.execute(sql, params)
        pass


