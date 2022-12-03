import numpy as np
from datetime import datetime, timedelta, timezone
from django.core.management.base import BaseCommand, CommandError

from shares.model.shares_name import SharesName
import numpy as np
from django.core.mail import send_mail
from shares.model.shares_industry import SharesIndustry


# 校验的
# 1. 检测当天板块 macd是否上升
# 2. 板块回踩10日均线
# 3. 寻找，该板块的股票下，回踩均线的股票


class Command(BaseCommand):
    help = '记录每天-10以下的kdj股票'


    def handle(self, *args, **options):
        send_data = {
            'buy': [],
            'sell': [],
        }
        for item in SharesName.objects.filter(status=1, code_type=2):
            code = item.code
            sharesListSource = SharesIndustry.objects.filter(code_id=code).order_by('-date_as')
            print(sharesListSource)
            sharesListSource3 = SharesIndustry.objects.filter(code_id=code, max_min_flag=1).order_by('-date_as')
            sharesListSource3 = np.array(sharesListSource3)[:3]
            for item2 in sharesListSource3:
                print(item2)
                if abs(sharesListSource[0].avg_p_min_rate - item2.avg_p_min_rate) < .2:
                    send_data['buy'].append(sharesListSource[0].code_id)
                    break
            print("---------------------------------")
        if len(send_data['buy']) > 0:
            self.sendMessage(send_data)

    def sendMessage(self, send_data):
        tz = timezone(timedelta(hours=+8))
        str_con = "支撑位板块代码：%s\n" % ("\",\"".join(send_data['buy']))
        send_mail(
            '触碰支撑位%s' % (datetime.now(tz)),
            str_con,
            'lovemeand1314@163.com',
            ['844596330@qq.com'],
            fail_silently=False,
        )