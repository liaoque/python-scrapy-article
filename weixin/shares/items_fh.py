# -*- coding: utf-8 -*-

# Define here the models for your scraped items
# 股票抓取
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
import datetime


class Items(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    code = scrapy.Field()
    title = scrapy.Field()
    info = scrapy.Field()
    amount = scrapy.Field()
    range = scrapy.Field()
    directors_date_as = scrapy.Field()
    shareholder_date_as = scrapy.Field()
    implement_date_as = scrapy.Field()
    register_date_as = scrapy.Field()
    ex_date_as = scrapy.Field()

    def save(self, cursor):
        code = self['code'][0]
        date_as = self['directors_date_as'][0]
        if self.exitsByCode(cursor, code, date_as):
            sql = """
            update mc_shares_fh 
                    set title = %s, info = %s, amount = %s,
                        `range` = %s, directors_date_as = %s, shareholder_date_as = %s 
                        `implement_date_as` = %s, register_date_as = %s, ex_date_as = %s 
                    where code_id = %s and date_as=%s
            """
            params = (
                self["title"][0],
                self["info"][0],
                self["amount"][0],
                self["range"][0],
                self["directors_date_as"][0],
                self["shareholder_date_as"][0],
                self["implement_date_as"][0],
                self["register_date_as"][0],
                self["ex_date_as"][0],
                code,
                date_as,
            )
            cursor.execute(sql, params)
            return
        sql = """
            INSERT INTO mc_shares_fh (code_id, title, info, amount, `range`, 
            directors_date_as, shareholder_date_as,
             implement_date_as, register_date_as, ex_date_as)
            VALUES (%s, %s, %s,  %s, %s)
            """;
        params = (
            code,
            self["title"][0],
            self["info"][0],
            self["amount"][0],
            self["range"][0],
            self["directors_date_as"][0],
            self["shareholder_date_as"][0],
            self["implement_date_as"][0],
            self["register_date_as"][0],
            self["ex_date_as"][0],
        )
        cursor.execute(sql, params)
        pass

    pass

    def exitsByCode(self, cursor, code, date_as):
        sql = "SELECT code_id FROM mc_shares_fh  WHERE code_id = %s and date_as=%s"
        cursor.execute(sql, (
            code,
            date_as,
        ));
        return cursor.rowcount > 0