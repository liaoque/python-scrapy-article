# -*- coding: utf-8 -*-

# Define here the models for your scraped items
# 股票抓取
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re

def strToFloat(s):
    try:
        return float(s)
    except ValueError:
        return 0

class Items(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    name = scrapy.Field()
    code = scrapy.Field()
    p_min = scrapy.Field()
    p_max = scrapy.Field()
    p_start = scrapy.Field()
    p_end = scrapy.Field()
    p_range = scrapy.Field()
    buy_count = scrapy.Field()
    buy_sum = scrapy.Field()
    date_as = scrapy.Field()
    temper_tonghuashun = scrapy.Field()
    area_id = scrapy.Field()
    temper_dongfangcaifu = scrapy.Field()
    master_buy_sell = scrapy.Field()
    master_buy_sum = scrapy.Field()
    area_map = {
        "SH": 1,
        "SZ": 2,
        "BJ": 3,
    }

    def save(self, cursor):
        code = self['code'][0]
        date_as = self['date_as'][0]
        if self.exitsByCode(cursor, code, date_as):
            return
        sql = """
            INSERT INTO mc_shares (
            name, code_id, p_min, p_max, p_start, p_end, p_range,
             buy_count, buy_sum, master_buy_sum, master_buy_sell, date_as
            )
            VALUES (%s, %s, %s,  %s,  %s, %s, %s,
             %s,  %s, %s,  %s,   %s)
            """;
        params = (
            self["name"][0],
            code,
            int(strToFloat(self["p_min"][0]) * 100),
            int(strToFloat(self["p_max"][0]) * 100),
            int(strToFloat(self["p_start"][0]) * 100),
            int(strToFloat(self["p_end"][0]) * 100),
            int(strToFloat(self["p_range"][0]) * 100),
            self["buy_count"][0],
            strToFloat(self["buy_sum"][0]) * 100,
            strToFloat(self["master_buy_sum"][0]) * 100,
            strToFloat(self["master_buy_sell"][0]) * 100,
            self["date_as"][0]
        )
        cursor.execute(sql, params)
        pass

    pass

    def findByCode(self, cursor, code, date_as):
        sql = "SELECT code_id FROM mc_shares  WHERE code_id = '%s' and date_as='%s'" % (code, date_as)
        cursor.execute(sql);
        return cursor

    def exitsByCode(self, cursor, code, date_as):
        sql = "SELECT code_id FROM mc_shares  WHERE code_id = '%s' and date_as='%s'" % (code, date_as)
        cursor.execute(sql);
        return cursor.rowcount
