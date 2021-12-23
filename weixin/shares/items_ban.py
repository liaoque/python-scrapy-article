# -*- coding: utf-8 -*-

# Define here the models for your scraped items
# 股票抓取
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re


class Items(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    code = scrapy.Field()
    avoid_cycle = scrapy.Field()
    remain_avoid_cycle = scrapy.Field()
    avoid_reason = scrapy.Field()
    date_as = scrapy.Field()

    def save(self, cursor):
        code = self['code'][0]
        date_as = self['date_as'][0]
        if self.exitsByCode(cursor, code, date_as):
            return
        sql = """
            INSERT INTO mc_shares_ban (code_id, avoid_cycle, remain_avoid_cycle, avoid_reason, date_as)
            VALUES (%s, %s, %s,  %s, %s)
            """;
        params = (
            code,
            self["avoid_cycle"][0],
            self["remain_avoid_cycle"][0],
            self["avoid_reason"][0],
            date_as
        )
        cursor.execute(sql, params)
        pass
    pass

    def exitsByCode(self, cursor, code, date_as):
        sql = "SELECT code_id FROM mc_shares_ban  WHERE code_id = '%s' and date_as='%s'" % (code, date_as)
        cursor.execute(sql);
        return cursor.rowcount