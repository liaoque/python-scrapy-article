

import scrapy
import json
from scrapy.loader import ItemLoader
import sys
import re
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi

import weixin.q6m5mdownurl.items as Q6m5mItems
import time

class Q6m5mdownurl(scrapy.Spider):
    name = 'q6m5mdownurl'
    allowed_domains = ['.6m5m.com']
    base_url = 'http://www.6m5m.com';
    start_urls = [ ]

    headers = {
        "HOST": "www.6m5m.com",
        "Cookie": "PHPSESSID=s96mjoqji3vhmt1a4mulnepae7; Hm_lvt_5f1bccc1006b0aa10014b15174ab2360=1573826663,1573826777; UM_distinctid=16e721d76abd8-001846f19817fc-67e1b3f-1fa400-16e721d76ac83a; CNZZDATA1277733598=622366333-1573868518-null%7C1573884990; Hm_lpvt_5f1bccc1006b0aa10014b15174ab2360=1573885140",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        'User-Agent':  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }

  

    def parse(self, response):
        pass

    def start_requests(self):

        # dbparms = dict(
        #     host = settings["MYSQL_HOST"],
        #     db = settings["MYSQL_DBNAME"],
        #     user = settings["MYSQL_USER"],
        #     passwd = settings["MYSQL_PASSWORD"],
        #     port = settings["MYSQL_PORT"],
        #     charset='utf8mb4',
        #     cursorclass=MySQLdb.cursors.DictCursor,
        #     use_unicode=True,
        # )
        # dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)


        db = MySQLdb.connect(host=self.settings.get('MYSQL_HOST'),
            user=self.settings.get('MYSQL_USER'),
            password=self.settings.get('MYSQL_PASSWORD'),
            database=self.settings.get('MYSQL_DBNAME'), 
            charset='utf8mb4' )
        # 使用cursor()方法获取操作游标 
        cursor = db.cursor()
        sql = 'select url from mc_6m5m where status is null';
        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 获取所有记录列表
            results = cursor.fetchall()
        except:
            print("Error: unable to fecth data")
        db.close()
        _list = []
        for url in results:
            # 替换url获取下载地址
            _url = re.sub('service-', 'shop_order-', url[0])
            _urtl = self.base_url + '/' + re.sub('.html', '-steps-step1-op-buy.html', _url)
            coo = 'PHPSESSID=s96mjoqji3vhmt1a4mulnepae7; Hm_lvt_5f1bccc1006b0aa10014b15174ab2360=1573826663,1573826777; UM_distinctid=16e721d76abd8-001846f19817fc-67e1b3f-1fa400-16e721d76ac83a; CNZZDATA1277733598=622366333-1573868518-null|1573884990; Hm_lpvt_5f1bccc1006b0aa10014b15174ab2360=1573872798'
            self.headers['Referer'] = self.base_url + '/' + url[0];
            yield scrapy.Request(_urtl, cookies=coo, headers=self.headers, callback=self.get_csrf_token)
        pass

    def get_csrf_token(self, response):
        href = response.css('#ddd::attr(href)').extract_first("")
        searchObj = re.search('file_path=(\S+)', href)
        href = searchObj.group(1)
        #二进制字符串转换
        referer = response.request.headers.getlist('Referer')[0].decode(encoding = "utf-8")


        url = re.sub('http://www.6m5m.com/', '', referer)
        item_loader = ItemLoader(item=Q6m5mItems.Items())

        # 文档标题
        item_loader.add_value("url", url)
        item_loader.add_value("zip_url", href)
        return item_loader.load_item()
        pass

pass