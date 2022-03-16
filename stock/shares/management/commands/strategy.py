import numpy as np
from datetime import datetime, date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares import Shares
# import numpy as np
# import talib
# import sys


# 交易策略
# 第一天买入500股，
#       第二天 跌3%，买入500股，
#           之后涨幅高于 当天的3%卖出 500股
#           之后跌超过6% 卖出 1000股, 并以第二天的收盘价购买500股
#           不满足以上两个条件， 收盘价卖出 500股
#       第二天 未跌3%，不发生买入和卖出交易

class Command(BaseCommand):
    help = '使用策略'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        for item in SharesName.objects.filter(status=1, code_type=1):
            code = item.code
            income = self.seek(code, "2021-12-31")
            print("%s 总收入 %s" % (code, income))
            break

    def seek(self, code, today):
        sharesToday = Shares.objects.filter(code_id=code, date_as__gt=today).order_by('date_as')
        if len(sharesToday) == 0:
            return 0
        sharesToday = sharesToday[0]
        total = sharesToday.p_end * 500
        income = 0
        while True:
            result = self.nextSeek(sharesToday)
            if result['stop'] == True:
                print("停止" % (sharesToday.date_as))
                break
            elif result['all'] == True:
                income += result['sell'] * 1000 - total - result['buy'] * 500
                print("%s全部抛售，当前收入 %s" % ( sharesToday.date_as,income))
                # 第二天开始重新轮回
                income += self.seek(code, result['sharesToday'].date_as)
            else:
                income += result['sell'] * 500 - result['buy'] * 500
                print("%s当前收入 %s" % (sharesToday.date_as, income))
            sharesToday = result['sharesToday']
        return income;

    def nextSeek(self, item):
        sharesToday = Shares.objects.filter(code_id=item.code, date_as__gt=item.date_as).order_by('date_as')
        if len(sharesToday) == 0:
            return {
                'all': False,
                'stop': True,
                'total': 0,
            }
        sharesToday = sharesToday[0]

        p_start = sharesToday.p_start
        buy = 0
        sell = 0
        if (p_start - sharesToday.p_min) / sharesToday.p_start > 0.03:
            # sharesToday.p_start - sharesToday.p_start *0.03 买入500
            buy = (sharesToday.p_start - sharesToday.p_start * 0.03)
            if (sharesToday.p_start - sharesToday.p_min) / sharesToday.p_start > 0.06:
                # 全部卖出
                sell = sharesToday.p_start - sharesToday.p_start * 0.06
            elif (sharesToday.p_max - sharesToday.p_start) / sharesToday.p_start > 0.03:
                #  sharesToday.p_start + sharesToday.p_start *0.03 卖出500
                sell = (sharesToday.p_start + sharesToday.p_start * 0.03)
            else:
                # 收盘价 卖出500
                sell = sharesToday.p_end
            pass
        else:
            pass
        return {
            'all': False,
            'stop': False,
            'sell': sell,
            'buy': buy,
            'sharesToday': sharesToday
        }
