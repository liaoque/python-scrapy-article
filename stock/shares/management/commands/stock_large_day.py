import numpy as np
from datetime import datetime, timedelta, timezone
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max, Min
from django.db import connection

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares import Shares
from shares.model.shares_industry import SharesIndustry
from shares.model.shares_industry_month import SharesIndustryMonth
import time
import requests
from shares.model.stock_members import SharesMembers
from shares.model.shares_date import SharesDate
from shares.model.shares_month import SharesMonth
from django.core.mail import send_mail


# import numpy as np
# import talib
# import sys

# 统计上班年和下班的 最高和最低


class Command(BaseCommand):
    help = ' 查股票放量'

    def handle(self, *args, **options):
        codeList = SharesName.getCodeList()
        codeLargeList = {
            "date": [],
            "month": [],
            "date2": [],
            "week2": [],
            "date3": [],
        }
        tz = timezone(timedelta(hours=+8))
        date_as = datetime.today().astimezone(tz).date()
        # 放量
        for item in codeList:
            sharesItem5 = Shares.objects.filter(code_id=item.code).order_by('-date_as')[:5]
            if sharesItem5[0].date_as != date_as:
                continue

            endCount = sharesItem5[0].buy_count
            count4 = sum([item.buy_count for item in sharesItem5[1:]]) / 4
            if endCount / count4 > 1.8:
                codeLargeList["date"].append(item.code)

        for item in codeList:
            sharesItem6 = SharesMonth.objects.filter(code_id=item.code).order_by('-p_year', '-p_month')[:2]
            if len(sharesItem6) < 2:
                continue

            if sharesItem6[0].p_month != datetime.today().astimezone(
                    tz).month or sharesItem6[0].p_year != datetime.today().astimezone(tz).year:
                continue
            if sharesItem6[0].buy_count / sharesItem6[1].buy_count > 2:
                codeLargeList["month"].append(item.code)

        # 缩量
        for item in codeList:
            sharesItem5 = Shares.objects.filter(code_id=item.code).order_by('-date_as')[:20]
            if len(sharesItem5) < 20:
                continue
            # if sharesItem5[0].date_as != date_as:
            #     continue

            endCount = sharesItem5[0].buy_count
            sharesItem5 = sharesItem5[:19]
            min_buy_count = min([item2.buy_count for item2 in sharesItem5])
            if min_buy_count / endCount > 1.5:
                codeLargeList["date2"].append(item.code)

        # 周六
        for item in codeList:
            if datetime.today().weekday() < 5:
                break
            cday = datetime.today() - timedelta(days=90)
            sql = "SELECT 1 as id, code_id, cast(UNIX_TIMESTAMP(date_as)/86400/7 as signed ) as week, sum(buy_count) as buy_count, date_as " \
                  "FROM `mc_shares` " \
                  "WHERE date_as > %s and code_id = %s GROUP by week"
            sharesItem5 = Shares.objects.raw(sql, params=(cday, item.code))
            sharesItem5 = sharesItem5[1:]
            endCount = sharesItem5[-1].buy_count
            sharesItem5 = sharesItem5[:-1]
            min_buy_count = min([item2.buy_count for item2 in sharesItem5])
            if min_buy_count / endCount > 1.5:
                codeLargeList["week2"].append(item.code)

        codeList = SharesName.objects.filter(code_type=1, status=1).all()
        for item in codeList:
            sharesItem5 = Shares.objects.filter(code_id=item.code).order_by('-date_as')[:20]
            if len(sharesItem5) < 20:
                continue
            # if sharesItem5[0].date_as != date_as:
            #     continue

            endCount = sharesItem5[0].buy_count
            sharesItem5 = sharesItem5[:19]
            min_buy_count = min([item2.buy_count for item2 in sharesItem5])
            if min_buy_count / endCount > 1.5:
                codeLargeList["date3"].append(item.code)

        self.sendMessage(codeLargeList)



    def sendMessage(self, send_data):
        if len(send_data['date']) == 0 and len(send_data['month']) == 0 \
                and len(send_data['date2']) == 0 and len(send_data['week2']) == 0 \
                and len(send_data['date3']) == 0:
            return

        tz = timezone(timedelta(hours=+8))
        str_con = "日放量股票：%s\n 月放量股票：%s\n" % (
            "\",\"".join(send_data['date']), "\",\"".join(send_data['month']))

        str_con += "\n日缩量股票：%s\n 周缩量股票：%s\n" % (
            "\",\"".join(send_data['date2']), "\",\"".join(send_data['week2']))

        str_con += "\na日缩量股票：%s\n " % (
            "\",\"".join(send_data['date3'])
        )
        send_mail(
            '放量提醒%s' % (datetime.now(tz)),
            str_con,
            'lovemeand1314@163.com',
            ['844596330@qq.com'],
            fail_silently=False,
        )
