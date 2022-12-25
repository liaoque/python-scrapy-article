import numpy as np
from datetime import datetime, timedelta, timezone
from django.core.management.base import BaseCommand, CommandError

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from django.core.mail import send_mail
import numpy as np
import talib
import math
import sys
from shares.model.shares_industry import SharesIndustry
from shares.model.shares_industry_week import SharesIndustryWeek


# 校验的
# 1. 检测当天板块 macd是否上升
# 2. 板块回踩10日均线
# 3. 寻找，该板块的股票下，回踩均线的股票


class Command(BaseCommand):
    help = '记录每天-10以下的kdj股票'

    codeList = []
    dateList = []
    five_start = ''
    twenty_start = ''
    sixty_start = ''
    one_hundred_start = ''
    four_year_start = ''

    date_as = None

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        for item in SharesName.objects.filter(status=1, code_type=2):
            code = item.code
            sharesListSource = SharesIndustry.objects.filter(code_id=code).order_by('date_as')
            i = 0
            between = 0
            up = True
            sharesListSource = np.array(sharesListSource)
            self.defMaxMin(sharesListSource, i + 1, up, between)

        send_data = {
            'buy': [],
            'sell': [],
        }
        send_data_week = {
            'buy': [],
            'sell': [],
        }
        for item in SharesName.objects.filter(status=1, code_type=2):
            code = item.code
            sharesListSource = SharesIndustry.objects.filter(code_id=code).order_by('-date_as')

            sharesListSource3 = SharesIndustry.objects.filter(code_id=code, max_min_flag=1).order_by('-date_as')
            sharesListSource3 = np.array(sharesListSource3)[:3]
            for item2 in sharesListSource3:
                if abs(sharesListSource[0].avg_p_min_rate - item2.avg_p_min_rate) < .2:
                    send_data['buy'].append(sharesListSource[0].code_id)
                    break

            sharesListSource3 = SharesIndustryWeek.objects.filter(code_id=code, max_min_flag=1).order_by('-date_as')
            sharesListSource3 = np.array(sharesListSource3)[:3]
            for item2 in sharesListSource3:
                sharesListSource = SharesIndustryWeek.objects.filter(code_id=code).order_by('-date_as')
                if abs(sharesListSource[0].avg_p_min_rate - item2.avg_p_min_rate) < .2:
                    send_data_week['buy'].append(sharesListSource[0].code_id)
                    break

        self.sendMessage(send_data, send_data_week)

    def sendMessage(self, send_data, send_data_week):
        if len(send_data['buy']) <= 0 and len(send_data_week['buy']) <= 0:
            return

        tz = timezone(timedelta(hours=+8))
        str_con = "买入方式，直接龙头，日线级别看三天，三天不涨马上走，\n " \
                  "周线级别， 1， 2， 6方式买入，承受3次支撑"

        if len(send_data['buy']) > 0:
            str_con = str_con + "日线级别支撑位板块代码：%s\n" % ("\",\"".join(send_data['buy']))
        if len(send_data['buy']) > 0:
            str_con = str_con + "周线级别支撑位板块代码：%s\n" % ("\",\"".join(send_data_week['buy']))
        send_mail(
            '触碰支撑位%s' % (datetime.now(tz)),
            str_con,
            'lovemeand1314@163.com',
            ['844596330@qq.com'],
            fail_silently=False,
        )

    def defMaxMin(self, sharesListSource, i, up, between):
        if len(sharesListSource) < 10:
            return
        sharesList = sharesListSource[i * 10:10 + i * 10]
        if len(sharesList) < 10:
            return
        lastIndex = len(sharesList) - 1
        print(sharesList)
        if up:
            p_start = min(sharesList[0].p_end, sharesList[0].p_start)
            if p_start > sharesList[lastIndex].p_end:
                # 趋势反转， 到了压力位
                between = maxIndustryIndex = self.max(sharesListSource, between, 10 + i * 10)
                maxIndustry = sharesListSource[maxIndustryIndex]
                maxIndustry.max_min_flag = -1
                maxIndustry.save()
                # sMaxIndustry = None
                up = False
            self.defMaxMin(sharesListSource, i + 1, up, between)
        else:
            p_start = max(sharesList[0].p_end, sharesList[0].p_start)
            if p_start < sharesList[lastIndex].p_end:
                # 趋势反转， 到了支撑位
                between = minIndustryIndex = self.min(sharesListSource, between, 10 + i * 10)
                minIndustry = sharesListSource[minIndustryIndex]
                minIndustry.max_min_flag = 1
                minIndustry.save()
                # sMaxIndustry = None
                up = True
            self.defMaxMin(sharesListSource, i + 1, up, between)

    def max(self, sharesList, start, end):
        c = end
        max2 = start
        i = start
        while i < c:
            if sharesList[max2].p_end < sharesList[i].p_end:
                max2 = i
            i = i + 1
        return max2

    def min(self, sharesList, start, end):
        # sharesList = sharesList[start:end]
        c = end
        min2 = start
        i = start
        while i < c:
            if sharesList[min2].p_end > sharesList[i].p_end:
                min2 = i
            i = i + 1
        return min2
