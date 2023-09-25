import numpy as np
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError

from shares.model.shares_name import SharesName
from shares.model.shares_week_macds import SharesWeekMacds
import numpy as np
import talib
import sys



class Command(BaseCommand):
    help = '计算各种指标'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        today = datetime.now().date().strftime('%Y-%m-%d')
        self.calculateKdj(today)
        # print("开始计算kdj-----")
        # today = datetime.now().date().strftime('%Y-%m-%d')
        # self.KdjCompute(today)
        pass

    def calculateKdj(self, today):
        # today = '2021-12-27'
        for item in SharesName.objects.filter(status=1, code_type=1):

            # 写过了
            code = item.code
            # 数据不存在
            itemList = item.shares_weeks_set.all()
            print(str(len(itemList)) +"---")
            if len(itemList) == 0:
                continue
            # 计算kdj
            macdDIFF1, macdDEA1, macd1 = self.talib_Macd(itemList)
            i = 0
            if len(macd1) > 10:
                i = len(macd1) -10
            while i < len(macd1):
                date_as = itemList[i].date_as
                sharesKdjList = SharesWeekMacds.objects.filter(code_id=code, date_as=date_as)
                if len(sharesKdjList):
                    i += 1
                    continue
                macdDIFF = macdDIFF1[i]
                macdDEA = macdDEA1[i]
                macd = macd1[i]
                i += 1
                if repr(macdDIFF) in ("inf", "nan") or repr(macdDEA) in ("inf", "nan") or repr(macd) in ("inf", "nan"):
                    print("计算出未知数据", (code, macdDIFF, macdDEA, macd))
                    sys.stdout.flush()
                    continue
                b = SharesWeekMacds(code_id=code, diff=macdDIFF, macd=macd, dea=macdDEA, cycle_type=1, date_as=date_as)
                b.save()
        pass

    def talib_Macd(self, data):
        # 计算kd指标
        close_prices = np.array([v.p_end / 100 for v in data])
        macdDIFF, macdDEA, macd = talib.MACDEXT(close_prices, fastperiod=12, fastmatype=1, slowperiod=26, slowmatype=1,
                                                signalperiod=9, signalmatype=1)
        macd = macd * 2
        return (macdDIFF, macdDEA, macd)
