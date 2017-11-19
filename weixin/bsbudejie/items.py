# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from weixin.utils.common import md5
from weixin.utils.htmlfilter import filter_tags

class Items(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 文档id
    # id = scrapy.Field()
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

    def insertDuanZi(self,cursor):
        body = self['body'][0]
        if body == '':
            return
        body = filter_tags(body)
        fingerprint = md5(body)

        sql = "select id from mc_duanzi where fingerprint = '%s'" % (fingerprint)
        cursor.execute(sql)
        if cursor.rowcount:
            return
        sql = """
                INSERT INTO mc_duanzi (body, fingerprint, status) VALUES ( %s, %s, %s)
            """
        params = (
            body,
            fingerprint,
            1
        )
        cursor.execute(sql, params)
    pass

    def insertVideo(self,cursor):
        src = self['src'][0]
        thumbnail = self['thumbnail'][0]
        title = self['title'][0]
        fingerprint = md5(src)
        sql = "select id from mc_video where fingerprint = '%s'" % (fingerprint)
        cursor.execute(sql)
        if cursor.rowcount:
            return
        sql = """
                INSERT INTO mc_video (title , src, thumbnail, fingerprint, status) 
                VALUES ( %s, %s, %s, %s, %s)
            """
        params = (
            title,
            src,
            thumbnail,
            fingerprint,
            1
        )
        cursor.execute(sql, params)
    pass

    def insertGif(self,cursor):
        src = self['src'][0]
        title = self['title'][0]
        fingerprint = md5(src)
        sql = "select id from mc_gif where fingerprint = '%s'" % (fingerprint)
        cursor.execute(sql)
        if cursor.rowcount:
            return
        sql = """
                INSERT INTO mc_gif (title, src, fingerprint, status) VALUES ( %s,  %s, %s, %s)
            """
        params = (
            title,
            src,
            fingerprint,
            1
        )
        cursor.execute(sql, params)
    pass

    def insertArticle(self, cursor):
        title = self['title'][0]
        src = self['src'][0]
        fingerprint = md5(src)
        sql = "SELECT fingerprint FROM unique_baisibudejie WHERE fingerprint = '%s'" % (fingerprint);
        cursor.execute(sql)
        if cursor.rowcount:
            return False
        sql = """
                  INSERT INTO unique_baisibudejie (fingerprint)
                  VALUES(%s)
                  """;
        params = (
            fingerprint,
        )
        if cursor.execute(sql, params):
            sql = """
                              INSERT INTO mc_article (title, thumbnail, status)
                              VALUES(%s, %s, %s)
                              """;
            params = (
                self["title"][0],
                src,
                1
            )
            result = cursor.execute(sql, params)
            if result:
                sql = """
                                  INSERT INTO mc_article_body (aid, body)
                                  VALUES(%s, %s)
                                  """;
                params = (
                    cursor.lastrowid,
                    '<img src="' + src + '"/>'
                )
                result = cursor.execute(sql, params)
            return result
    pass

    def save(self, cursor):
        type = self['type'][0]
        if type == 1:
            self.insertVideo(cursor)
        elif type == 2:
            if self['src'][0].find('.gif') > 0 :
                self.insertGif(cursor)
            else:
                self.insertArticle(cursor)
        elif type == 3:
                self.insertDuanZi(cursor)
    pass

