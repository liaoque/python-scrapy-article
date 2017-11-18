# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join


class Items(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 文档id
    id = scrapy.Field()
    # 缩略图
    thumbnail = scrapy.Field()
    # 标题
    title = scrapy.Field()
    # 关键字
    key_words = scrapy.Field()
    # 内容
    body = scrapy.Field()
    # 文章类型
    article_type = scrapy.Field()
    # 文档URL
    view_url = scrapy.Field()
    # 作者名字
    author_name = scrapy.Field()
    # 作者头像
    author_face = scrapy.Field()
    # api接口
    cur_url = scrapy.Field()
    # 指纹
    fingerprint = scrapy.Field()

    def insertBaoZouRiBao(self, cursor):
        id = self["id"]
        sql = "SELECT id FROM baozouribao WHERE id = %d" % (id);
        cursor.execute(sql)
        if cursor.rowcount:
            return False
        sql = """
                                  INSERT INTO baozouribao (id, view_url, article_type)
                                  VALUES(%s, %s, %s)
                                  """;
        params = (
            id,
            self["view_url"],
            self["article_type"]
        )
        return  cursor.execute(sql, params)

    def insertArticle(self, cursor):
        sql = """
                  INSERT INTO article (title, thumbnail, status)
                  VALUES(%s, %s, %s)
                  """;
        params = (
            self["title"],
            self["thumbnail"],
            1
        )
        result = cursor.execute(sql, params)
        if result:
            sql = """
                      INSERT INTO article_body (aid, body)
                      VALUES(%s, %s)
                      """;
            params = (
                cursor.lastrowid,
                self["body"]
            )
            result = cursor.execute(sql, params)
        return result

    def save(self, cursor):
        if self.insertBaoZouRiBao(cursor):
            self.insertArticle(cursor)
    pass

