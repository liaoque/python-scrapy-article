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
    stock_code = scrapy.Field()
    name = scrapy.Field()
    industry = scrapy.Field()
    today_zdf = scrapy.Field()
    five_zdf = scrapy.Field()
    ten_zdf = scrapy.Field()
    twenty_zdf = scrapy.Field()
    sixty_zdf = scrapy.Field()

    def save(self, cursor):
        id = self['id'][0]
        if self.exitsById(cursor, id):
            sql = """
            update mc_shares_ban set 
                today_zdf = %s, five_zdf = %s, ten_zdf = %s, 
                twenty_zdf = %s, sixty_zdf = %s
                where id = %s
            """
            params = (
                int(self["today_zdf"][0]) * 100,
                int(self["five_zdf"][0]) * 100,
                int(self["ten_zdf"][0]) * 100,
                int(self["twenty_zdf"][0]) * 100,
                int(self["sixty_zdf"][0]) * 100,
                id,
            )
            cursor.execute(sql, params)
            return
        else:
            sql = """
                INSERT INTO mc_shares_ban (
                id, code, name, industry
                , today_zdf, five_zdf, ten_zdf, twenty_zdf
                , sixty_zdf
                )
                VALUES (%s, %s, %s,  %s, %s
                , %s, %s,  %s, %s, %s
                )
                """;
            params = (
                id,
                self["code"][0],
                self["name"][0],
                self["industry"][0],
                self["today_zdf"][0],
                self["five_zdf"][0],
                self["ten_zdf"][0],
                self["twenty_zdf"][0],
                self["sixty_zdf"][0],
            )
            cursor.execute(sql, params)

        stock_code = self['stock_code'][0]
        if self.exitsByCode(cursor, id) != 0:
            sql = """
                    INSERT INTO mc_futrues_join_shares (
                    code, futrues_id)
                    VALUES (%s, %s)
                    """;
            params = (
                stock_code,
                id
            )
            cursor.execute(sql, params)

    pass

    def exitsById(self, cursor, id):
        sql = "SELECT id FROM mc_futrues_hot  WHERE id = '%s' " % (id)
        cursor.execute(sql);
        return cursor.rowcount


    def exitsByCode(self, cursor, code):
        sql = "SELECT id FROM mc_futrues_join_shares  WHERE code = '%s' " % (code)
        cursor.execute(sql);
        return cursor.rowcount