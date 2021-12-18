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
    area_map = {
        "SH": 1,
        "SZ": 2,
        "BJ": 3,
    }

    def save(self, cursor):

        code = self['code'][0]
        if 'area_id' in self:
            self.save_one(cursor)
            return
        if 'temper_tonghuashun' in self:
            self.save_temper_tonghuashun(cursor)
            return
        if 'temper_dongfangcaifu' in self:
            self.save_temper_dongfangcaifu(cursor)
            return

        date_as = self['date_as'][0]
        sql = "SELECT id FROM mc_shares  WHERE code = '%s' and date_as='%s'" % (code, date_as)
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

    def save_one(self, cursor):
        code = self['code'][0]
        area_id = int(self.area_map[self['area_id'][0]])
        print(self['area_id'][0], area_id)
        cursor = self.findByCode(cursor, code)
        if cursor.rowcount:
            data = cursor.fetchall()
            print(data)
            if data[0][0] != 0:
                sql = "update mc_shares_name set area_id = '%s'  WHERE code = %s" % (area_id, code)
                cursor.execute(sql);

        sql = """
                    INSERT INTO mc_shares_name (name, code, area_id)
                    VALUES (%s, %s, %s)
                    """;
        params = (
            self["name"][0],
            code,
            area_id,
        )
        cursor.execute(sql, params)

    def save_temper_tonghuashun(self, cursor):
        code = self['code'][0]
        temper_tonghuashun = self['temper_tonghuashun'][0]
        sql = "update mc_shares_name set temper_tonghuashun = '%d'  WHERE code = %s" % (temper_tonghuashun, code)
        cursor.execute(sql);

    def save_temper_dongfangcaifu(self, cursor):
        code = self['code'][0]
        temper_dongfangcaifu = self['temper_dongfangcaifu'][0]
        sql = "update mc_shares_name set temper_dongfangcaifu = '%d'  WHERE code = %s" % (
            temper_dongfangcaifu, code)
        cursor.execute(sql);

    def findByCode(self, cursor, code):
        sql = "SELECT area_id FROM mc_shares_name  WHERE code = '%s'" % code
        cursor.execute(sql);
        return cursor