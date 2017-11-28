# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from weixin.utils.common import md5


class Items(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    thumbnail = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()
    view_url = scrapy.Field()
    fingerprint = scrapy.Field()
    # type 1文章， 2写真
    type = scrapy.Field()

    def insertQiuShiBaiKe(self, cursor):
        id = self["id"]
        sql = "SELECT id FROM mc_unique_qiushibaike WHERE id = %d" % (id);
        cursor.execute(sql)
        if cursor.rowcount:
            return False
        sql = """
                  INSERT INTO mc_unique_qiushibaike (id, view_url, type)
                  VALUES(%s, %s, %s)
                  """;
        params = (
            id,
            self["view_url"],
            self["type"]
        )
        return cursor.execute(sql, params)

    def insertArticle(self, cursor):
        if self.insertQiuShiBaiKe(cursor) == False:
            return False
        sql = """
                  INSERT INTO mc_article (title, thumbnail, status)
                  VALUES(%s, %s, %s)
                  """;
        params = (
            self["title"],
            self["thumbnail"],
            1
        )
        result = cursor.execute(sql, params)
        if result:
            pid = cursor.lastrowid;
            sql = """
                      INSERT INTO mc_article_body (aid, body)
                      VALUES(%s, %s)
                      """;
            params = (
                pid,
                self["body"]
            )
            result = cursor.execute(sql, params)
            sql = """
                   update mc_unique_qiushibaike set pid = '%d' WHERE id = '%s'
               """ % (pid, self["id"])
            cursor.execute(sql)
        return result

    def save(self, cursor):
        result = False
        if self['type'] == 1:
            result = self.insertArticle(cursor)
        elif self['type'] == 2:
            result = self.insertXieZhen(cursor)
        return result

    def insertXieZhen(self, cursor):
        title = self["title"]
        fingerprint = md5(title)
        sql = "SELECT fingerprint FROM mc_unique_xiezhen WHERE fingerprint = '%s'" % (fingerprint);
        cursor.execute(sql)
        if cursor.rowcount:
            return False
        sql = """
                  INSERT INTO mc_unique_xiezhen (fingerprint, view_url, type)
                  VALUES(%s, %s, %s)
                  """;
        params = (
            fingerprint,
            self["view_url"],
            1
        )
        result = cursor.execute(sql, params)
        if result:
            sql = """
                      INSERT INTO mc_xiezhen (title, thumbnail,  status)
                      VALUES(%s, %s, %s)
                      """;
            params = (
                self["title"],
                self["thumbnail"],
                1
            )
            result = cursor.execute(sql, params)
            if result:
                pid = cursor.lastrowid;
                sql = """
                          INSERT INTO mc_image_list (pid, src, type)
                          VALUES(%s, %s, %s)
                          """;
                params = [ (pid, image, 1 ) for image in self["body"]]
                # print(sql, params)
                result = cursor.executemany(sql, params)
                sql = """
                    update mc_unique_xiezhen set pid = '%d' WHERE fingerprint = '%s'
                """ % (pid, fingerprint)
                cursor.execute(sql)
        return result
