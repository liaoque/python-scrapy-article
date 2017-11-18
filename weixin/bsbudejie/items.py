# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from weixin.utils.common import md5

class Items(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 文档id
    id = scrapy.Field()
    # 缩略图
    thumbnail = scrapy.Field()
    # 标题
    title = scrapy.Field()
    # 图片连接
    src = scrapy.Field()

    # 内容
    body = scrapy.Field()
    # 文章类型 1.视频, 2,GIF, 3.段子
    type = scrapy.Field()

    # 指纹
    fingerprint = scrapy.Field()

    def insertVideo(self, cursor):
        sql = ""
    pass

    def insertGif(self, cursor):

        sql = ""
    pass

    def insertDuanZi(self,cursor):
        body = self['body'][0]
        fingerprint = md5(body)

        sql = "select id from duanzi where fingerprint = '%s'" % (fingerprint)
        cursor.execute(sql)
        if cursor.rowcount:
            return
        sql = """
                INSERT INTO duanzi (body, fingerprint, status) VALUES ( %s, %s, %s)
            """
        params = (
            body,
            fingerprint,
            1
        )
        cursor.execute(sql, params)
    pass

    def insertVideo(self,cursor):
        body = self['src'][0]
        fingerprint = md5(body)
        sql = "select id from video where fingerprint = '%s'" % (fingerprint)
        cursor.execute(sql)
        if cursor.rowcount:
            return
        sql = """
                INSERT INTO video (src, fingerprint, status) VALUES ( %s, %s, %s)
            """
        params = (
            body,
            fingerprint,
            1
        )
        cursor.execute(sql, params)
    pass

    def insertGif(self,cursor):
        body = self['body'][0]
        fingerprint = md5(body)
        sql = "select id from gif where fingerprint = '%s'" % (fingerprint)
        cursor.execute(sql)
        if cursor.rowcount:
            return
        sql = """
                INSERT INTO duanzi (body, fingerprint, status) VALUES ( %s, %s, %s)
            """
        params = (
            body,
            fingerprint,
            1
        )
        cursor.execute(sql, params)
    pass

    def save(self, cursor):
        if self['type'] == 1:
            self.insertVideo(cursor)
        elif self['type'] == 2:
            self.insertGif(cursor)
        elif self['type'] == 3:
            self.insertDuanZi(cursor)
    pass

