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
    industry_code_id = scrapy.Field()
    code_id = scrapy.Field()


    def save(self, cursor):
        code_id = self['code_id'][0]
        industry_code_id = self['industry_code_id'][0]
        if self.exitsByCode(cursor, code_id, industry_code_id):
            return
        sql = """
            INSERT INTO mc_shares_industry (code_id, industry_code_id)
            VALUES (%s, %s)
            """;
        params = (
            code_id,
            industry_code_id,
        )
        cursor.execute(sql, params)
        pass
    pass

    def exitsByCode(self, cursor, code_id, industry_code_id):
        sql = "SELECT code_id FROM mc_shares_industry  WHERE code_id = '%s' and industry_code_id='%s'" % (code_id, industry_code_id)
        cursor.execute(sql);
        return cursor.rowcount