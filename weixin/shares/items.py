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
    status = scrapy.Field()
    code_type = scrapy.Field()
    area_map = {
        "SH": 1,
        "SZ": 2,
        "BJ": 3,
    }

    def save(self, cursor):
        if 'area_id' in self:
            self.save_one(cursor)
            return
        if 'temper_tonghuashun' in self:
            self.save_temper_tonghuashun(cursor)
            return
        if 'temper_dongfangcaifu' in self:
            self.save_temper_dongfangcaifu(cursor)
            return

    pass

    def save_one(self, cursor):
        code = self['code'][0]
        status = self['status'][0]
        code_type = self['code_type'][0]
        area_id = int(self.area_map[self['area_id'][0]])
        cursor = self.findByCode(cursor, code)
        if cursor.rowcount:
            data = cursor.fetchall()
            if data[0]['area_id'] != 0:
                sql = "update mc_shares_name set area_id = '%s'  WHERE code = '%s'" % (area_id, code)
                cursor.execute(sql);
            if data[0]['status'] != status:
                sql = "update mc_shares_name set status = '%s' WHERE code = '%s'" % (status, code)
                cursor.execute(sql);
            if data[0]['code_type'] != 0:
                sql = "update mc_shares_name set code_type = '%s'  WHERE code = '%s'" % (code_type, code)
                cursor.execute(sql);
            return
        sql = """
                    INSERT INTO mc_shares_name (name, code, area_id, code_type)
                    VALUES (%s, %s, %s, %s)
                    """;
        params = (
            self["name"][0],
            code,
            area_id,
            code_type,
        )
        cursor.execute(sql, params)

    def save_temper_tonghuashun(self, cursor):
        code = self['code'][0]
        temper_tonghuashun = self['temper_tonghuashun'][0]
        sql = "update mc_shares_name set temper_tonghuashun = '%d'  WHERE code = '%s'" % (temper_tonghuashun, code)
        cursor.execute(sql);

    def save_temper_dongfangcaifu(self, cursor):
        code = self['code'][0]
        temper_dongfangcaifu = self['temper_dongfangcaifu'][0]
        sql = "update mc_shares_name set temper_dongfangcaifu = '%d'  WHERE code = '%s'" % (
            temper_dongfangcaifu, code)
        cursor.execute(sql);

    def findByCode(self, cursor, code):
        sql = "SELECT area_id,status,code_type FROM mc_shares_name  WHERE code = '%s'" % code
        cursor.execute(sql);
        return cursor
