# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.loader import ItemLoader
import sys

import time
import MySQLdb
import MySQLdb.cursors
import weixin.shares.items_finance as SharesItems
import copy


# import baozouribao.items

# from scrapy.spiders import CrawlSpider, Rule
# from scrapy.linkextractors import LinkExtractor

class SharesFinance(scrapy.Spider):
    name = 'shares_finance'

    allowed_domains = ['.eastmoney.com']
    start_urls = []
    headers = {
        "HOST": "emweb.securities.eastmoney.com",
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
    }
    db = None
    cursor = None

    def connect(self):
        if self.db == None:
            self.db = MySQLdb.connect(host=self.settings.get('MYSQL_HOST'),
                                      user=self.settings.get('MYSQL_USER'),
                                      password=self.settings.get('MYSQL_PASSWORD'),
                                      database=self.settings.get('MYSQL_DBNAME'),
                                      charset='utf8mb4')
            self.cursor = self.db.cursor()

    def get_url_zcfzb(self, code, dates):
        return 'https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/zcfzbAjaxNew?' \
               'companyType=4&reportDateType=0&reportType=1&dates=' + dates + \
               '&code=' + code

    def get_url_lrb(self, code, dates):
        return 'https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/zcfzbAjaxNew?' \
               'companyType=4&reportDateType=0&reportType=1&dates=' + dates + \
               '&code=' + code

    def get_url(self, code):
        return 'https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/ZYZBAjaxNew?type=0&code=' + code


    def start_requests(self):
        self.connect()
        results = self.findStoks()
        for item in results:
            code = item[0]
            if int(code) < 600000:
                s_code = 'SZ' +code
            else:
                s_code = 'SH' + code
            url = self.get_url(s_code)
            self.headers['s_code'] = s_code
            yield scrapy.Request(url,
                                 headers=self.headers,
                                 dont_filter=True,
                                 callback=self.parse_content)

    def parse_content(self, response):
        result = json.loads(response.text)
        for item in result["data"]:
            headers = {}
            # print(str(item))
            headers['XSMLL'] = str(item['XSMLL'])
            headers['XSJLL'] = str(item['XSJLL'])
            headers['ZZCZZTS'] = str(item['ZZCZZTS'])
            headers['CHZZTS'] = str(item['CHZZTS'])
            headers['YSZKZZTS'] = str(item['YSZKZZTS'])
            headers['TOAZZL'] = str(item['TOAZZL'])
            headers['CHZZL'] = str(item['CHZZL'])
            headers['YSZKZZL'] = str(item['YSZKZZL'])

            s_code = response.request.headers.getlist('s_code')[0].decode("UTF-8")
            url = self.get_url_zcfzb(s_code, str(item['REPORT_DATE']))
            yield scrapy.Request(url,
                                 headers=headers,
                                 dont_filter=True,
                                 callback=self.parse_zcfzb)

    # 资产负债表
    def parse_zcfzb(self, response):
        result = json.loads(response.text)
        for item in result["data"]:
            headers = {}
            headers['XSMLL'] = response.request.headers.getlist('XSMLL')[0].decode("UTF-8")
            headers['XSJLL'] = response.request.headers.getlist('XSJLL')[0].decode("UTF-8")
            headers['ZZCZZTS'] = response.request.headers.getlist('ZZCZZTS')[0].decode("UTF-8")
            headers['CHZZTS'] = response.request.headers.getlist('CHZZTS')[0].decode("UTF-8")
            headers['YSZKZZTS'] = response.request.headers.getlist('YSZKZZTS')[0].decode("UTF-8")
            headers['TOAZZL'] = response.request.headers.getlist('TOAZZL')[0].decode("UTF-8")
            headers['CHZZL'] = response.request.headers.getlist('CHZZL')[0].decode("UTF-8")
            headers['YSZKZZL'] = response.request.headers.getlist('YSZKZZL')[0].decode("UTF-8")
            headers['NOTE_ACCOUNTS_PAYABLE'] = str(item['NOTE_ACCOUNTS_PAYABLE'])
            headers['NOTE_ACCOUNTS_RECE'] = str(item['NOTE_ACCOUNTS_RECE'])
            headers['PREPAYMENT'] = str(item['PREPAYMENT'])
            s_code = response.request.headers.getlist('s_code')[0].decode("UTF-8")
            url = self.parse_lrb(s_code, str(item['REPORT_DATE']))
            yield scrapy.Request(url,
                                 headers=self.headers,
                                 dont_filter=True,
                                 callback=self.parse_lrb)

    # 利润表
    def parse_lrb(self, response):
        result = json.loads(response.text)
        for item in result["data"]:
            headers = {}
            headers['XSMLL'] = response.request.headers.getlist('XSMLL')[0].decode("UTF-8")
            headers['XSJLL'] = response.request.headers.getlist('XSJLL')[0].decode("UTF-8")
            headers['ZZCZZTS'] = response.request.headers.getlist('ZZCZZTS')[0].decode("UTF-8")
            headers['CHZZTS'] = response.request.headers.getlist('CHZZTS')[0].decode("UTF-8")
            headers['YSZKZZTS'] = response.request.headers.getlist('YSZKZZTS')[0].decode("UTF-8")
            headers['TOAZZL'] = response.request.headers.getlist('TOAZZL')[0].decode("UTF-8")
            headers['CHZZL'] = response.request.headers.getlist('CHZZL')[0].decode("UTF-8")
            headers['YSZKZZL'] = response.request.headers.getlist('YSZKZZL')[0].decode("UTF-8")
            headers['NOTE_ACCOUNTS_PAYABLE'] = response.request.headers.getlist('NOTE_ACCOUNTS_PAYABLE')[0].decode("UTF-8")
            headers['NOTE_ACCOUNTS_RECE'] = response.request.headers.getlist('NOTE_ACCOUNTS_RECE')[0].decode("UTF-8")
            headers['PREPAYMENT'] = response.request.headers.getlist('PREPAYMENT')[0].decode("UTF-8")
            headers['NONBUSINESS_INCOME'] = str(item['NONBUSINESS_INCOME'])
            headers['NONBUSINESS_EXPENSE'] = str(item['NONBUSINESS_EXPENSE'])
            headers['INVEST_INCOME'] = str(item['INVEST_INCOME'])
            item_loader = ItemLoader(item=SharesItems.Items())
            item_loader.add_value("SECURITY_CODE", headers['SECURITY_CODE'])
            item_loader.add_value("REPORT_DATE", headers['REPORT_DATE'])
            item_loader.add_value("XSMLL", headers['XSMLL'])
            item_loader.add_value("REPORT_DATE_NAME", headers['REPORT_DATE_NAME'])
            item_loader.add_value("XSJLL", headers['XSJLL'])
            item_loader.add_value("ZZCZZTS", headers['ZZCZZTS'])
            item_loader.add_value("CHZZTS", headers['CHZZTS'])
            item_loader.add_value("YSZKZZTS", headers['YSZKZZTS'])
            item_loader.add_value("TOAZZL", headers['TOAZZL'])
            item_loader.add_value("CHZZL", headers['CHZZL'])
            item_loader.add_value("YSZKZZL", headers['YSZKZZL'])
            item_loader.add_value("NOTE_ACCOUNTS_PAYABLE", headers['NOTE_ACCOUNTS_PAYABLE'])
            item_loader.add_value("NOTE_ACCOUNTS_RECE", headers['NOTE_ACCOUNTS_RECE'])
            item_loader.add_value("PREPAYMENT", headers['PREPAYMENT'])
            item_loader.add_value("NONBUSINESS_INCOME", headers['NOTE_ACCOUNTS_PAYABLE'])
            item_loader.add_value("NONBUSINESS_EXPENSE", headers['NONBUSINESS_INCOME'])
            item_loader.add_value("INVEST_INCOME", headers['INVEST_INCOME'])
            yield item_loader.load_item()

    def findStoks(self):
        sql = 'select code,name,area_id from mc_shares_name where status = 1 and code_type =1';
        results = []
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 获取所有记录列表
            results = self.cursor.fetchall()
        except:
            print("Error: unable to fecth data")
        return results


    def __del__(self):
        if self.db != None:
            self.cursor.close()
            self.db.close()
