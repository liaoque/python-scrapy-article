import numpy as np
from datetime import datetime, timedelta, timezone
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

from shares.model.shares_name import SharesName
from shares.model.shares import Shares
from shares.model.shares_fh import SharesFH
from shares.model.shares_macd import SharesMacd
from shares.model.shares_kdj import SharesKdj

import requests
from django.core.mail import send_mail


# " /bin/cp /alidata/python/python-scrapy-article/stock/* /alidata/python/python-scrapy-article-master/stock -rf"


class Command(BaseCommand):
    help = '分红检测'

    all = {

    }

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        tz = timezone(timedelta(hours=+8))
        today = datetime.now().astimezone(tz).date().strftime('%Y-%m-%d')
        self.calculateCheck(today)
        # self.calculate("2022-05-30")
        pass

    def calculateCheck(self, today):

        for item in SharesName.objects.filter(status=1, code_type=1):
            # 写过了
            code = item.code

            if not (code < '300000' or ('300000' < code < '600000') or (
                    '600000' < code < '700000')):
                continue

            json2 = SharesFH.objects.filter(code_id=code)
            if len(json2) == 0:
                continue

            for item in json2:
                # if item.directors_date_as is not None:
                #     self.checkShares(item.directors_date_as, code, "directors_date_as")
                # if datetime.strftime(item.directors_date_as, '%Y-%m-%d') > '2022-04-19' and datetime.strftime(
                #         item.directors_date_as, '%Y-%m-%d') < '2022-04-27':
                #     self.checkShares(item.directors_date_as, code, "directors_date_as")

                # if item.shareholder_date_as is not None:
                #     self.checkShares(item.shareholder_date_as, code, "shareholder_date_as")
                # if datetime.strftime(item.shareholder_date_as, '%Y-%m-%d') > '2022-04-19' and datetime.strftime(
                #         item.shareholder_date_as, '%Y-%m-%d') < '2022-04-27':
                #     self.checkShares(item.shareholder_date_as, code, "shareholder_date_as")

                if item.implement_date_as is not None and item.register_date_as is not None:
                    date_as = item.implement_date_as + timedelta(1)
                    self.checkSharesBetween(date_as, item.register_date_as, code, "implement_date_as")
                    # if datetime.strftime(item.implement_date_as, '%Y-%m-%d') > '2022-04-19' and datetime.strftime(
                    #         item.implement_date_as, '%Y-%m-%d') < '2022-04-27':
                    #     self.checkShares(item.implement_date_as, code, "implement_date_as")

                # if item.register_date_as is not None:
                #     date_as = item.register_date_as - timedelta(1)
                #     self.checkShares(date_as, code, "register_date_as")
                # if datetime.strftime(item.register_date_as, '%Y-%m-%d') > '2022-04-19' and datetime.strftime(
                #         item.register_date_as, '%Y-%m-%d') < '2022-04-27':
                #     date_as = item.register_date_as - timedelta(1)
                #     self.checkShares(date_as, code, "register_date_as")

                # if item.ex_date_as is not None:
                #     self.checkShares(item.ex_date_as, code, "ex_date_as")
                # if datetime.strftime(item.ex_date_as, '%Y-%m-%d') > '2022-04-19' and datetime.strftime(
                #         item.ex_date_as, '%Y-%m-%d') < '2022-04-27':
                #     self.checkShares(item.ex_date_as, code, "ex_date_as")
                break

        print(self.all)
        pass

    def checkSharesBetween(self, column, column2, code, date_as):
        if date_as not in self.all:
            self.all[date_as] = {
                "up": 0,
                "low": 0,
            }
        itemAll = Shares.objects.filter(date_as=column, code_id=code)
        if len(itemAll) == 0:
            return
        itemAll2 = Shares.objects.filter(date_as=column2, code_id=code)
        if len(itemAll2) == 0:
            return
        if itemAll[0].p_end < itemAll2[0].p_end:
            self.all[date_as]["up"] += 1
        else:
            self.all[date_as]["low"] += 1

    def checkShares(self, column, code, date_as):
        if date_as not in self.all:
            self.all[date_as] = {
                "up": 0,
                "low": 0,
            }
        itemAll = Shares.objects.filter(date_as=column, code_id=code)
        if len(itemAll) == 0:
            return
        for item3 in itemAll:
            print(item3)
            if item3.p_start < item3.p_end:
                self.all[date_as]["up"] += 1
            else:
                self.all[date_as]["low"] += 1

    def checkSharesMacd(self, column, code, date_as):
        if date_as not in self.all:
            self.all[date_as] = {
                "up": 0,
                "low": 0,
            }
        # itemAll = SharesMacd.objects.filter(date_as__lt=column, code_id=code).order_by('-date_as')
        itemAll = SharesKdj.objects.filter(date_as__lt=column, code_id=code).order_by('-date_as')
        if len(itemAll) <= 1:
            return
        itemAll = itemAll[:2]
        # if itemAll[0].macd < itemAll[1].macd:
        if itemAll[0].j < itemAll[1].j:
            return
        self.checkShares(column, code, date_as)

    def getUrl(self, item):
        area_map = {
            1: "SH",
            2: "SZ",
            3: "BJ",
        }
        return "https://emweb.securities.eastmoney.com/BonusFinancing/PageAjax?code=%s%s" % (
            area_map[item.area_id], item.code)

    def calculate(self, today):
        tz = timezone(timedelta(hours=+8))
        hour = datetime.now().astimezone(tz).hour

        self.all["directors_date_as"] = []
        shareholder_date_as = SharesFH.objects.filter(shareholder_date_as=today)
        self.appendCode(shareholder_date_as, "shareholder_date_as")

        implement_date_as = SharesFH.objects.filter(implement_date_as=today)
        self.appendCode(implement_date_as, "implement_date_as")

        today2 = datetime.strptime(today, '%Y-%m-%d').date() + timedelta(1)
        if hour > 15:
            today2 = datetime.strptime(today, '%Y-%m-%d').date() + timedelta(2)
        register_date_as = SharesFH.objects.filter(register_date_as=today2)
        # print(register_date_as, datetime.strptime(today, '%Y-%m-%d').date(), today2)
        self.appendCode(register_date_as, "register_date_as")

        today2 = today
        if hour > 15:
            today2 = datetime.strptime(today, '%Y-%m-%d').date() + timedelta(1)
        ex_date_as = SharesFH.objects.filter(ex_date_as=today2)
        self.appendCode(ex_date_as, "ex_date_as")

        # all = {
        #     "directors_date_as": [],
        #     "shareholder_date_as": [],
        #     "implement_date_as": [],
        #     "register_date_as": [],
        #     "ex_date_as": []
        # }
        # for item in SharesName.objects.filter(status=1, code_type=1):
        #     # 写过了
        #     code = item.code
        #     json2 = SharesFH.objects.filter(code_id=code).order_by('-directors_date_as')
        #     if len(json2) == 0:
        #         continue
        #     item = json2[0]
        #     if item.directors_date_as is not None and item.directors_date_as == today:
        #         all['directors_date_as'].append(code)
        #
        #     if item.shareholder_date_as is not None and item.shareholder_date_as == today:
        #         all['shareholder_date_as'].append(code)
        #
        #     if item.implement_date_as is not None and item.implement_date_as == today:
        #         all['implement_date_as'].append(code)
        #
        #     if item.register_date_as is not None and item.register_date_as == today:
        #         all['register_date_as'].append(code)
        #
        #     if item.ex_date_as is not None and item.ex_date_as == today:
        #         all['ex_date_as'].append(code)

        self.sendMessage(self.all)
        pass

    def appendCode(self, implement_date_as, column):
        if column not in self.all:
            self.all[column] = []
        if len(implement_date_as) == 0:
            return
        for item in implement_date_as:
            code = item.code_id
            if not (code < '300000' or ('600000' < code < '700000')):
                continue
            self.all[column].append(code)

    def sendMessage(self, send_data):
        tz = timezone(timedelta(hours=+8))
        str = "董事会日期：%s\n 股东大会预案公告日期：%s\n 实施公告日：%s\n A股股权登记日：%s\n A股除权除息日：%s\n" % (
            "\",\"".join(send_data['directors_date_as']),
            "\",\"".join(send_data['shareholder_date_as']),
            "\",\"".join(send_data['implement_date_as']),
            "\",\"".join(send_data['register_date_as']),
            "\",\"".join(send_data['ex_date_as']))
        send_mail(
            '分红%s' % (datetime.now(tz)),
            str,
            'lovemeand1314@163.com',
            ['844596330@qq.com'],
            fail_silently=False,
        )
