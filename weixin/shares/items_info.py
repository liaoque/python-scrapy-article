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
    pe = scrapy.Field()
    pb = scrapy.Field()
    pe_d = scrapy.Field()
    pe_ttm = scrapy.Field()
    gpm = scrapy.Field()
    npmos = scrapy.Field()
    roe = scrapy.Field()
    gpm_ex = scrapy.Field()
    npmos_ex = scrapy.Field()
    type = scrapy.Field()

    def save(self, cursor):
        if self['type'][0] == 'gpm':
            self.save_pb(cursor)
        elif self['type'][0] == 'pe_ttm':
            self.save_pe(cursor)
        else:
            self.save_gpm_ex(cursor)

    pass

    def save_pb(self, cursor):
        code = self['code'][0]
        pb = self['pb'][0]
        # pe = self['pe'][0]
        pe_d = self['pe_d'][0]
        # pe_ttm = self['pe_ttm'][0]
        gpm = self['gpm'][0]
        npmos = self['npmos'][0]
        roe = self['roe'][0]
        sql = "update mc_shares_name set pb = '%s', pe_d = '%s', " \
              " gpm = '%s', npmos = '%s', roe = '%s'  WHERE code = '%s'" % (
                  pb, pe_d, gpm, npmos, roe, code)
        cursor.execute(sql)

    def save_gpm_ex(self, cursor):
        code = self['code'][0]
        gpm_ex = self['gpm_ex'][0]
        npmos_ex = self['npmos_ex'][0]
        sql = "update mc_shares_name set gpm_ex = '%s', npmos_ex = '%s' WHERE code = '%s'" % (
            gpm_ex, npmos_ex, code
        )
        cursor.execute(sql)


    def save_pe(self, cursor):
        code = self['code'][0]
        pe_ttm = self['pe_ttm'][0]
        pe = self['pe'][0]
        sql = "update mc_shares_name set pe = '%s', pe_ttm = '%s' WHERE code = '%s'" % (
            pe, pe_ttm, code
        )
        cursor.execute(sql)

    def findByCode(self, cursor, code):
        sql = "SELECT * FROM mc_shares_name  WHERE code = '%s'" % code
        cursor.execute(sql);
        return cursor
