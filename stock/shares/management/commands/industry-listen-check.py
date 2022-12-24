import numpy as np
from datetime import datetime, timedelta, timezone
from django.core.management.base import BaseCommand, CommandError

from shares.model.shares_name import SharesName
import numpy as np
from django.core.mail import send_mail
from shares.model.shares_industry import SharesIndustry
from shares.model.shares_industry_macd import SharesIndustryMacd
from shares.model.shares_industry_week import SharesIndustryWeek


# 校验的
# 1. 检测当天板块 macd是否上升
# 2. 板块回踩10日均线
# 3. 寻找，该板块的股票下，回踩均线的股票


class Command(BaseCommand):
    help = '支撑位板块代码检测'

    def handle(self, *args, **options):
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
            sharesListSource3 = SharesIndustry.objects.filter(code_id=code, max_min_flag=1).order_by('-date_as')
            sharesListSource3 = np.array(sharesListSource3)[:3]
            for item2 in sharesListSource3:
                sharesListSource = SharesIndustry.objects.filter(code_id=code).order_by('-date_as')
                sharesIndustryMacd = SharesIndustryMacd.objects.filter(code_id=code,
                                                                       date_as=sharesListSource[0].date_as).order_by(
                    '-date_as')
                if abs(sharesListSource[0].avg_p_min_rate - item2.avg_p_min_rate) < .2 \
                        and sharesIndustryMacd[0].macd >= 0:
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
