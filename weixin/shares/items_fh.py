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
        title = self['title'][0]
        if len(self["info"]) == 0:
            self["info"][0] = None
        if len(self["amount"]) == 0:
            self["amount"][0] = None
        if len(self["range"]) == 0:
            self["range"][0] = None
        if len(self["directors_date_as"]) == 0:
            self["directors_date_as"][0] = None
        if len(self["shareholder_date_as"]) == 0:
            self["shareholder_date_as"][0] = None
        if len(self["implement_date_as"]) == 0:
            self["implement_date_as"][0] = None
        if len(self["register_date_as"]) == 0:
            self["register_date_as"][0] = None
        if len(self["ex_date_as"]) == 0:
            self["ex_date_as"][0] = None

        if self.exitsByCode(cursor, code, title):
            sql = """
            update mc_shares_fh 
                    set info = %s, amount = %s,
                        `range` = %s, directors_date_as = %s, shareholder_date_as = %s 
                        `implement_date_as` = %s, register_date_as = %s, ex_date_as = %s 
                    where code_id = %s and title=%s
            """
            params = (
                self["info"][0],
                self["amount"][0],
                self["range"][0],
                self["directors_date_as"][0],
                self["shareholder_date_as"][0],
                self["implement_date_as"][0],
                self["register_date_as"][0],
                self["ex_date_as"][0],
                code,
                title,
            )
            cursor.execute(sql, params)
            return
        sql = """
            INSERT INTO mc_shares_fh (code_id, title, info, amount, `range`, 
            directors_date_as, shareholder_date_as,
             implement_date_as, register_date_as, ex_date_as)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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

    def exitsByCode(self, cursor, code, title):
        sql = "SELECT code_id FROM mc_shares_fh  WHERE code_id = %s and title=%s"
        cursor.execute(sql, (
            code,
            title,
        ));
        return cursor.rowcount > 0
