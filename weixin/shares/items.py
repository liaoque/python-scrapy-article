# -*- coding: utf-8 -*-

# Define here the models for your scraped items
# 股票抓取
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
    temper_dongfangcaifu = scrapy.Field()


    def save(self, cursor):
        code = self['code'][0]

        if 'temper_tonghuashun' in self:
            temper_tonghuashun = self['temper_tonghuashun'][0]
            sql = "update mc_shares_name set temper_tonghuashun = '%d'  WHERE code = %s" % (temper_tonghuashun, code)
            cursor.execute(sql);
            return


        if 'temper_dongfangcaifu' in self:
            temper_dongfangcaifu = self['temper_dongfangcaifu'][0]
            sql = "update mc_shares_name set temper_dongfangcaifu = '%d'  WHERE code = %s" % (temper_dongfangcaifu, code)
            # print(sql)
            cursor.execute(sql);
            return

        date_as = self['date_as'][0]
        sql = "SELECT code FROM mc_shares_name  WHERE code = '%s'" % code

        cursor.execute(sql);
        if cursor.rowcount != 1:
            sql = """
            INSERT INTO mc_shares_name (name, code)
            VALUES (%s, %s)
            """;
            params = (
                self["name"][0],
                code
            )
            cursor.execute(sql, params)
        pass   

        sql = "SELECT id FROM mc_shares  WHERE code = '%s' and date_as='%s'" % (code, date_as)
        # print(self)
        cursor.execute(sql);
        if cursor.rowcount:
            return
        sql = """
            INSERT INTO mc_shares (name, code, p_min, p_max, p_start, p_end, p_range, buy_count, buy_sum, date_as)
            VALUES (%s, %s, %s,  %s,  %s, %s, %s, %s,  %s,  %s)
            """;
        params = (
            self["name"][0],
            code,
            int(float(self["p_min"][0]) * 100),
            int(float(self["p_max"][0]) * 100),
            int(float(self["p_start"][0]) * 100),
            int(float(self["p_end"][0]) * 100),
            int(float(self["p_range"][0]) * 100),
            self["buy_count"][0],
            float(self["buy_sum"][0]) * 100,
            self["date_as"][0]
        )
        cursor.execute(sql, params)
        pass
    pass


