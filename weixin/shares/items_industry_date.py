# -*- coding: utf-8 -*-

# Define here the models for your scraped items
# 股票抓取
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re


class Items(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    code = scrapy.Field()
    p_min = scrapy.Field()
    p_max = scrapy.Field()
    p_start = scrapy.Field()
    p_end = scrapy.Field()
    date_as = scrapy.Field()


    def save(self, cursor):
        code = self['code'][0]
        date_as = self['date_as'][0]
        if self.exitsByCode(cursor, code, date_as):
            return
        sql = """
            INSERT INTO mc_shares_industry (code_id, p_min, p_max, p_start, p_end, date_as)
            VALUES (%s, %s, %s,  %s,  %s, %s)
            """;
        params = (
            code,
            int(float(self["p_min"][0]) * 100),
            int(float(self["p_max"][0]) * 100),
            int(float(self["p_start"][0]) * 100),
            int(float(self["p_end"][0]) * 100),
            self["date_as"][0]
        )
        cursor.execute(sql, params)
        pass
    pass

    def findByCode(self, cursor, code, date_as):
        sql = "SELECT code_id FROM mc_shares_industry  WHERE code_id = '%s' and date_as='%s'" % (code, date_as)
        cursor.execute(sql);
        return cursor

    def exitsByCode(self, cursor, code, date_as):
        sql = "SELECT code_id FROM mc_shares_industry  WHERE code_id = '%s' and date_as='%s'" % (code, date_as)
        cursor.execute(sql);
        return cursor.rowcount