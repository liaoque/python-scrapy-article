# -*- coding: utf-8 -*-

# Define here the models for your scraped items
# 股票抓取
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
import datetime


class Items(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    SECURITY_CODE = scrapy.Field()
    REPORT_DATE = scrapy.Field()
    REPORT_DATE_NAME = scrapy.Field()
    XSMLL = scrapy.Field()
    XSJLL = scrapy.Field()
    ZZCZZTS = scrapy.Field()
    CHZZTS = scrapy.Field()
    YSZKZZTS = scrapy.Field()
    TOAZZL = scrapy.Field()
    CHZZL = scrapy.Field()
    YSZKZZL = scrapy.Field()
    NOTE_ACCOUNTS_PAYABLE = scrapy.Field()
    NOTE_ACCOUNTS_RECE = scrapy.Field()
    PREPAYMENT = scrapy.Field()
    NONBUSINESS_INCOME = scrapy.Field()
    NONBUSINESS_EXPENSE = scrapy.Field()
    INVEST_INCOME = scrapy.Field()

    def defaults(self):
        s = ["SECURITY_CODE", "REPORT_DATE", "REPORT_DATE_NAME",
             "XSMLL",  "XSJLL",  "ZZCZZTS",  "CHZZTS",  "YSZKZZTS",
             "TOAZZL",  "CHZZL",  "YSZKZZL",  "NOTE_ACCOUNTS_PAYABLE",  "NOTE_ACCOUNTS_RECE",
             "PREPAYMENT",  "NOTE_ACCOUNTS_PAYABLE",  "NONBUSINESS_INCOME",
             "NONBUSINESS_EXPENSE", "INVEST_INCOME",]
        for item in s:
            if item not in self:
                self[item] = [0]
            if self[item][0] is None or self[item][0] == 'None':
                self[item] = [0]




    def save(self, cursor):
        code = self['SECURITY_CODE'][0]
        date_as = self['REPORT_DATE'][0]
        self.defaults()
        if self.exitsByCode(cursor, code, date_as):
            self.updateByCode(cursor)
        else:
            self.insertByCode(cursor)

    def exitsByCode(self, cursor, code, date_as):
        sql = "SELECT code_id FROM mc_shares_finance  WHERE code_id = %s and date_as=%s"
        cursor.execute(sql, (
            code,
            date_as,
        ));
        return cursor.rowcount > 0

    def updateByCode(self, cursor):
        sql = """
                update mc_shares_finance 
                        set  gpm = %s, `npmos` = %s, 
                        turnover_days = %s, goods_turnover_days = %s, `account_turnover_days` = %s, 
                        turnover_rate = %s, goods_turnover_rate = %s, `account_turnover_rate` = %s, 
                        non_operating_incom = %s, non_operating_expenses = %s, `income_from_investment` = %s,
                         notes_payable = %s, notes_receivable = %s , prepayment = %s 
                        where code_id = %s and date_as=%s
                """
        params = (
            self['XSMLL'][0],
            self['XSJLL'][0],
            self['ZZCZZTS'][0],
            self['CHZZTS'][0],
            self['YSZKZZTS'][0],
            self['TOAZZL'][0],
            self['CHZZL'][0],
            self['YSZKZZL'][0],

            self['NONBUSINESS_INCOME'][0],
            self['NONBUSINESS_EXPENSE'][0],
            self['INVEST_INCOME'][0],

            self['NOTE_ACCOUNTS_PAYABLE'][0],
            self['NOTE_ACCOUNTS_RECE'][0],
            self['PREPAYMENT'][0],



            self['SECURITY_CODE'][0],
            self['REPORT_DATE'][0],
        )
        print(self['PREPAYMENT'][0])
        cursor.execute(sql, params)

    def insertByCode(self, cursor):
        sql = """
                    INSERT INTO mc_shares_finance (code_id, title, date_as, gpm, `npmos`, 
                    turnover_days, goods_turnover_days,account_turnover_days,
                    turnover_rate, goods_turnover_rate,account_turnover_rate,
                    non_operating_incom, non_operating_expenses,income_from_investment,
                    notes_payable, notes_receivable, prepayment)
                    VALUES (
                    %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s
                    )
                    """;
        params = (

            self['SECURITY_CODE'][0],
            self['REPORT_DATE_NAME'][0],
            self['REPORT_DATE'][0],

            self['XSMLL'][0],
            self['XSJLL'][0],
            self['ZZCZZTS'][0],
            self['CHZZTS'][0],
            self['YSZKZZTS'][0],
            self['TOAZZL'][0],
            self['CHZZL'][0],
            self['YSZKZZL'][0],


            self['NONBUSINESS_INCOME'][0],
            self['NONBUSINESS_EXPENSE'][0],
            self['INVEST_INCOME'][0],

            self['NOTE_ACCOUNTS_PAYABLE'][0],
            self['NOTE_ACCOUNTS_RECE'][0],
            self['PREPAYMENT'][0],


        )
        print(self['PREPAYMENT'][0])
        cursor.execute(sql, params)
